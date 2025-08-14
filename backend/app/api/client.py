import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.api import bp
from app.models import ClientTicket, Ticket, User
from app import db
import sqlalchemy as sa

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/client/submit-ticket', methods=['POST'])
def submit_client_ticket():
    """Allow external clients to submit tickets without authentication"""
    try:
        # Handle both form data and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json() or {}
            files = {}
        
        # Validate required fields
        required_fields = ['name', 'surname', 'phone', 'email', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field.title()} is required'}), 400
        
        # Handle file uploads
        uploaded_files = []
        if files:
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file_key in files:
                file = files[file_key]
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent conflicts
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    uploaded_files.append(filename)
        
        # Create client ticket
        client_ticket = ClientTicket(
            name=data['name'],
            surname=data['surname'],
            phone=data['phone'],
            email=data['email'],
            description=data['description'],
            images=','.join(uploaded_files) if uploaded_files else None
        )
        
        db.session.add(client_ticket)
        db.session.flush()  # Get the ID
        
        # Create associated internal ticket
        ticket_title = f"Client Ticket from {data['name']} {data['surname']}"
        ticket = Ticket(
            title=ticket_title,
            description=f"Client: {data['name']} {data['surname']}\n"
                       f"Email: {data['email']}\n"
                       f"Phone: {data['phone']}\n\n"
                       f"Description:\n{data['description']}",
            status='Open',
            priority='Medium',
            created_by_id=None  # Client submissions have no user
        )
        
        db.session.add(ticket)
        db.session.flush()
        
        # Link them
        client_ticket.ticket_id = ticket.id
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket submitted successfully',
            'ticket_id': ticket.id,
            'reference_number': f"CT{client_ticket.id:06d}"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting client ticket: {str(e)}")
        return jsonify({'message': 'Failed to submit ticket'}), 500

@bp.route('/client/ticket-status/<reference_number>', methods=['GET'])
def get_client_ticket_status(reference_number):
    """Allow clients to check their ticket status using reference number"""
    try:
        # Extract ID from reference number (format: CT000001)
        if not reference_number.startswith('CT'):
            return jsonify({'message': 'Invalid reference number format'}), 400
        
        try:
            client_ticket_id = int(reference_number[2:])
        except ValueError:
            return jsonify({'message': 'Invalid reference number format'}), 400
        
        client_ticket = db.session.get(ClientTicket, client_ticket_id)
        if not client_ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        ticket_status = 'Open'
        if client_ticket.ticket:
            ticket_status = client_ticket.ticket.status
        
        return jsonify({
            'reference_number': reference_number,
            'status': ticket_status,
            'submitted_at': client_ticket.created_at.isoformat(),
            'description': client_ticket.description[:100] + '...' if len(client_ticket.description) > 100 else client_ticket.description
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting client ticket status: {str(e)}")
        return jsonify({'message': 'Failed to retrieve ticket status'}), 500
