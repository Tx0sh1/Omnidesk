import json
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, Ticket, ClientTicket, TicketCategory, AuditLog
from app import db, mail
from app.utils import validate_ticket_data, sanitize_html, get_client_ip, get_user_agent, paginate_query
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
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get filter parameters
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        category_filter = request.args.get('category', type=int)
        assigned_to_filter = request.args.get('assigned_to', type=int)
        search = request.args.get('search', '').strip()
        
        # Build base query with proper eager loading
        query = sa.select(Ticket).where(
            Ticket.is_deleted == False
        ).options(
            sa.orm.joinedload(Ticket.created_by),
            sa.orm.joinedload(Ticket.assigned_to),
            sa.orm.joinedload(Ticket.category),
            sa.orm.joinedload(Ticket.client_ticket)
        )
        
        # Apply filters
        if status_filter:
            query = query.where(Ticket.status == status_filter)
        
        if priority_filter:
            query = query.where(Ticket.priority == priority_filter)
        
        if category_filter:
            query = query.where(Ticket.category_id == category_filter)
        
        if assigned_to_filter:
            query = query.where(Ticket.assigned_to_id == assigned_to_filter)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.where(
                sa.or_(
                    Ticket.title.ilike(search_term),
                    Ticket.description.ilike(search_term),
                    Ticket.ticket_number.ilike(search_term)
                )
            )
        
        # Apply user-based filtering (non-admin users see only their tickets)
        if not user.is_admin:
            query = query.where(
                sa.or_(
                    Ticket.created_by_id == current_user_id,
                    Ticket.assigned_to_id == current_user_id
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Ticket.created_at.desc())
        
        # Execute query and get results
        tickets_query = db.session.scalars(query)
        
        # Paginate results
        pagination_info = paginate_query(tickets_query, page, per_page)
        tickets = pagination_info['items']
        
        current_app.logger.info(f"Found {len(tickets)} tickets for user {user.username}")
        
        tickets_data = []
        for ticket in tickets:
            try:
                ticket_data = {
                    'id': ticket.id,
                    'ticket_number': getattr(ticket, 'ticket_number', f'TKT-{ticket.id}'),
                    'title': ticket.title,
                    'description': ticket.description,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                    'created_by': None,
                    'assigned_to': None,
                    'category': None,
                    'client_info': None,
                    'sla_status': None,
                    'comment_count': 0,
                    'attachment_count': 0
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
                
                # Safely handle category relationship
                if hasattr(ticket, 'category') and ticket.category:
                    ticket_data['category'] = {
                        'id': ticket.category.id,
                        'name': ticket.category.name,
                        'color': ticket.category.color
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
                        'company': getattr(ticket.client_ticket, 'company', ''),
                        'reference_number': getattr(ticket.client_ticket, 'reference_number', f'CT{ticket.client_ticket.id:06d}'),
                        'images': images
                    }
                
                # Add SLA status if available
                if hasattr(ticket, 'get_sla_status'):
                    ticket_data['sla_status'] = ticket.get_sla_status().value
                
                # Add counts if available
                if hasattr(ticket, 'comments'):
                    ticket_data['comment_count'] = len([c for c in ticket.comments if not c.is_deleted])
                
                if hasattr(ticket, 'attachments'):
                    ticket_data['attachment_count'] = len(ticket.attachments)
                
                tickets_data.append(ticket_data)
                
            except Exception as e:
                current_app.logger.error(f"Error processing ticket {ticket.id}: {str(e)}")
                continue
        
        current_app.logger.info(f"Successfully serialized {len(tickets_data)} tickets")
        
        return jsonify({
            'tickets': tickets_data,
            'pagination': {
                'page': pagination_info['page'],
                'per_page': pagination_info['per_page'],
                'total': pagination_info['total'],
                'total_pages': pagination_info['total_pages'],
                'has_prev': pagination_info['has_prev'],
                'has_next': pagination_info['has_next'],
                'prev_page': pagination_info['prev_page'],
                'next_page': pagination_info['next_page']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in get_tickets: {str(e)}")
        return jsonify({'message': 'Internal server error occurred while fetching tickets'}), 500

@bp.route('/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate input data
    validation = validate_ticket_data(data)
    if not validation['is_valid']:
        return jsonify({
            'message': 'Validation failed',
            'errors': validation['errors']
        }), 400
    
    # Sanitize HTML content
    title = sanitize_html(data['title'].strip())
    description = sanitize_html(data['description'].strip())
    
    # Validate category if provided
    category_id = data.get('category_id')
    category = None
    if category_id:
        category = db.session.get(TicketCategory, category_id)
        if not category or not category.is_active:
            return jsonify({'message': 'Invalid category'}), 400
    
    # Validate assigned user if provided
    assigned_to_id = data.get('assigned_to_id')
    assigned_to = None
    if assigned_to_id:
        assigned_to = db.session.get(User, assigned_to_id)
        if not assigned_to or not assigned_to.is_active:
            return jsonify({'message': 'Invalid assigned user'}), 400
    
    try:
        ticket = Ticket(
            title=title,
            description=description,
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Open'),
            created_by_id=current_user_id,
            assigned_to_id=assigned_to_id,
            category_id=category_id,
            estimated_hours=data.get('estimated_hours')
        )
        
        db.session.add(ticket)
        db.session.flush()  # Get the ID
        
        # Create audit log
        audit_log = AuditLog(
            action='CREATED',
            details=f"Created ticket: {title}",
            user_id=current_user_id,
            ticket_id=ticket.id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_number': getattr(ticket, 'ticket_number', f'TKT-{ticket.id}'),
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'color': category.color
                } if category else None,
                'assigned_to': {
                    'id': assigned_to.id,
                    'username': assigned_to.username
                } if assigned_to else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating ticket: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        ticket = db.session.get(Ticket, ticket_id)
        
        if not ticket or getattr(ticket, 'is_deleted', False):
            current_app.logger.warning(f"Ticket {ticket_id} not found")
            return jsonify({'message': 'Ticket not found'}), 404
        
        # Check permissions
        if not user.is_admin and ticket.created_by_id != current_user_id and ticket.assigned_to_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        ticket_data = {
            'id': ticket.id,
            'ticket_number': getattr(ticket, 'ticket_number', f'TKT-{ticket.id}'),
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
            'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
            'resolved_at': ticket.resolved_at.isoformat() if getattr(ticket, 'resolved_at', None) else None,
            'closed_at': ticket.closed_at.isoformat() if getattr(ticket, 'closed_at', None) else None,
            'created_by': None,
            'assigned_to': None,
            'category': None,
            'client_info': None,
            'sla_status': None,
            'estimated_hours': getattr(ticket, 'estimated_hours', None),
            'actual_hours': getattr(ticket, 'actual_hours', None),
            'resolution_notes': getattr(ticket, 'resolution_notes', None)
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
        
        if hasattr(ticket, 'category') and ticket.category:
            ticket_data['category'] = {
                'id': ticket.category.id,
                'name': ticket.category.name,
                'color': ticket.category.color,
                'sla_hours': getattr(ticket.category, 'sla_hours', None)
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
                'company': getattr(ticket.client_ticket, 'company', ''),
                'reference_number': getattr(ticket.client_ticket, 'reference_number', f'CT{ticket.client_ticket.id:06d}'),
                'images': images
            }
        
        # Add SLA status if available
        if hasattr(ticket, 'get_sla_status'):
            ticket_data['sla_status'] = ticket.get_sla_status().value
        
        return jsonify(ticket_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in get_ticket: {str(e)}")
        return jsonify({'message': 'Internal server error occurred while fetching ticket'}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    ticket = db.session.get(Ticket, ticket_id)
    data = request.get_json()
    
    if not ticket or getattr(ticket, 'is_deleted', False):
        return jsonify({'message': 'Ticket not found'}), 404
    
    # Check permissions
    if not user.is_admin and ticket.created_by_id != current_user_id and ticket.assigned_to_id != current_user_id:
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        changes = []
        
        # Update fields if provided and valid
        if 'title' in data:
            validation = validate_ticket_data({'title': data['title'], 'description': ticket.description})
            if validation['is_valid']:
                new_title = sanitize_html(data['title'].strip())
                if new_title != ticket.title:
                    changes.append(f"Title changed from '{ticket.title}' to '{new_title}'")
                    ticket.title = new_title
        
        if 'description' in data:
            validation = validate_ticket_data({'title': ticket.title, 'description': data['description']})
            if validation['is_valid']:
                new_description = sanitize_html(data['description'].strip())
                if new_description != ticket.description:
                    changes.append("Description updated")
                    ticket.description = new_description
        
        if 'status' in data and data['status'] in ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Cancelled']:
            if data['status'] != ticket.status:
                changes.append(f"Status changed from '{ticket.status}' to '{data['status']}'")
                old_status = ticket.status
                ticket.status = data['status']
                
                # Set resolved/closed timestamps
                if data['status'] == 'Resolved' and old_status != 'Resolved':
                    ticket.resolved_at = datetime.utcnow()
                elif data['status'] == 'Closed' and old_status != 'Closed':
                    ticket.closed_at = datetime.utcnow()
        
        if 'priority' in data and data['priority'] in ['Low', 'Medium', 'High', 'Critical']:
            if data['priority'] != ticket.priority:
                changes.append(f"Priority changed from '{ticket.priority}' to '{data['priority']}'")
                ticket.priority = data['priority']
        
        if 'assigned_to_id' in data:
            new_assigned_id = data['assigned_to_id'] if data['assigned_to_id'] != 0 else None
            if new_assigned_id != ticket.assigned_to_id:
                if new_assigned_id:
                    assigned_user = db.session.get(User, new_assigned_id)
                    if assigned_user and assigned_user.is_active:
                        changes.append(f"Assigned to {assigned_user.username}")
                        ticket.assigned_to_id = new_assigned_id
                else:
                    changes.append("Unassigned")
                    ticket.assigned_to_id = None
        
        if 'category_id' in data:
            new_category_id = data['category_id'] if data['category_id'] != 0 else None
            if new_category_id != getattr(ticket, 'category_id', None):
                if new_category_id:
                    category = db.session.get(TicketCategory, new_category_id)
                    if category and category.is_active:
                        changes.append(f"Category changed to {category.name}")
                        ticket.category_id = new_category_id
                        # Recalculate SLA dates based on new category
                        if hasattr(ticket, 'calculate_sla_dates'):
                            ticket.calculate_sla_dates()
                else:
                    changes.append("Category removed")
                    ticket.category_id = None
        
        # Update time tracking fields (admin only)
        if user.is_admin:
            if 'estimated_hours' in data:
                ticket.estimated_hours = data['estimated_hours']
            if 'actual_hours' in data:
                ticket.actual_hours = data['actual_hours']
            if 'resolution_notes' in data:
                ticket.resolution_notes = sanitize_html(data['resolution_notes']) if data['resolution_notes'] else None
        
        # Update timestamp
        ticket.updated_at = datetime.utcnow()
        
        # Create audit log if there were changes
        if changes:
            audit_log = AuditLog(
                action='UPDATED',
                details='; '.join(changes),
                user_id=current_user_id,
                ticket_id=ticket_id,
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )
            db.session.add(audit_log)
        
        db.session.commit()
        
        # Return updated ticket data
        return jsonify({
            'message': 'Ticket updated successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_number': getattr(ticket, 'ticket_number', f'TKT-{ticket.id}'),
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'assigned_to': {
                    'id': ticket.assigned_to.id,
                    'username': ticket.assigned_to.username
                } if ticket.assigned_to else None,
                'category': {
                    'id': ticket.category.id,
                    'name': ticket.category.name,
                    'color': ticket.category.color
                } if hasattr(ticket, 'category') and ticket.category else None,
                'updated_at': ticket.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating ticket {ticket_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

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
