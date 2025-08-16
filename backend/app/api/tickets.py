import json
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, Ticket, ClientTicket
from app import db, mail
import sqlalchemy as sa
from datetime import datetime
from flask_mail import Message

@bp.route('/tickets', methods=['GET'])
@jwt_required()
def get_tickets():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            current_app.logger.error(f"User not found for ID: {current_user_id}")
            return jsonify({'message': 'User not found'}), 404
        
        # Get all tickets with proper eager loading to avoid N+1 queries
        tickets = db.session.scalars(
            sa.select(Ticket)
            .options(
                sa.orm.joinedload(Ticket.created_by),
                sa.orm.joinedload(Ticket.assigned_to),
                sa.orm.joinedload(Ticket.client_ticket)
            )
        ).all()
        
        current_app.logger.info(f"Found {len(tickets)} tickets for user {user.username}")
        
        tickets_data = []
        for ticket in tickets:
            try:
                ticket_data = {
                    'id': ticket.id,
                    'title': ticket.title,
                    'description': ticket.description,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'created_by': None,
                    'assigned_to': None,
                    'client_info': None
                }
                
                # Safely handle created_by relationship
                if ticket.created_by:
                    ticket_data['created_by'] = {
                        'id': ticket.created_by.id,
                        'username': ticket.created_by.username
                    }
                
                # Safely handle assigned_to relationship
                if ticket.assigned_to:
                    ticket_data['assigned_to'] = {
                        'id': ticket.assigned_to.id,
                        'username': ticket.assigned_to.username
                    }
                
                # Safely handle client_ticket relationship
                if ticket.client_ticket:
                    try:
                        images = json.loads(ticket.client_ticket.images) if ticket.client_ticket.images else []
                    except (json.JSONDecodeError, TypeError) as e:
                        current_app.logger.warning(f"Failed to parse images for ticket {ticket.id}: {e}")
                        images = []
                    
                    ticket_data['client_info'] = {
                        'name': ticket.client_ticket.name,
                        'surname': ticket.client_ticket.surname,
                        'email': ticket.client_ticket.email,
                        'phone': ticket.client_ticket.phone,
                        'images': images
                    }
                
                tickets_data.append(ticket_data)
                
            except Exception as e:
                current_app.logger.error(f"Error processing ticket {ticket.id}: {str(e)}")
                # Continue processing other tickets even if one fails
                continue
        
        current_app.logger.info(f"Successfully serialized {len(tickets_data)} tickets")
        return jsonify({'tickets': tickets_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in get_tickets: {str(e)}")
        return jsonify({'message': 'Internal server error occurred while fetching tickets'}), 500

@bp.route('/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({'message': 'Title and description are required'}), 400
    
    ticket = Ticket(
        title=data['title'],
        description=data['description'],
        priority=data.get('priority', 'Medium'),
        status=data.get('status', 'Open'),
        created_by_id=current_user_id,
        assigned_to_id=data.get('assigned_to_id')
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify({
        'message': 'Ticket created successfully',
        'ticket': {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else None
        }
    }), 201

@bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    try:
        ticket = db.session.get(Ticket, ticket_id)
        
        if not ticket:
            current_app.logger.warning(f"Ticket {ticket_id} not found")
            return jsonify({'message': 'Ticket not found'}), 404
        
        ticket_data = {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
            'created_by': None,
            'assigned_to': None,
            'client_info': None
        }
        
        # Safely handle relationships
        if ticket.created_by:
            ticket_data['created_by'] = {
                'id': ticket.created_by.id,
                'username': ticket.created_by.username
            }
        
        if ticket.assigned_to:
            ticket_data['assigned_to'] = {
                'id': ticket.assigned_to.id,
                'username': ticket.assigned_to.username
            }
        
        if ticket.client_ticket:
            try:
                images = json.loads(ticket.client_ticket.images) if ticket.client_ticket.images else []
            except (json.JSONDecodeError, TypeError) as e:
                current_app.logger.warning(f"Failed to parse images for ticket {ticket.id}: {e}")
                images = []
            
            ticket_data['client_info'] = {
                'name': ticket.client_ticket.name,
                'surname': ticket.client_ticket.surname,
                'email': ticket.client_ticket.email,
                'phone': ticket.client_ticket.phone,
                'images': images
            }
        
        return jsonify(ticket_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in get_ticket: {str(e)}")
        return jsonify({'message': 'Internal server error occurred while fetching ticket'}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    data = request.get_json()
    
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    # Update ticket fields
    if 'title' in data:
        ticket.title = data['title']
    if 'description' in data:
        ticket.description = data['description']
    if 'status' in data:
        ticket.status = data['status']
    if 'priority' in data:
        ticket.priority = data['priority']
    if 'assigned_to_id' in data:
        ticket.assigned_to_id = data['assigned_to_id'] if data['assigned_to_id'] != 0 else None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Ticket updated successfully',
        'ticket': {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'assigned_to': {
                'id': ticket.assigned_to.id,
                'username': ticket.assigned_to.username
            } if ticket.assigned_to else None
        }
    }), 200

@bp.route('/tickets/<int:ticket_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    data = request.get_json()
    
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404
    
    if not data or not data.get('message'):
        return jsonify({'message': 'Message is required'}), 400
    
    # Send email to client if email exists
    if ticket.client_ticket and ticket.client_ticket.email:
        try:
            msg = Message(
                subject=f"Response to your support ticket #{ticket.id}",
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@omnidesk.com'),
                recipients=[ticket.client_ticket.email]
            )
            msg.body = (
                f"Dear {ticket.client_ticket.name},\n\n"
                f"{data['message']}\n\n"
                "Best regards,\nSupport Team"
            )
            mail.send(msg)
            
            return jsonify({'message': 'Response sent to client via email'}), 200
        except Exception as e:
            return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500
    
    return jsonify({'message': 'No client email found for this ticket'}), 400
