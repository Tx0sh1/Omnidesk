from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, Ticket, TicketComment, AuditLog
from app import db
from app.utils import sanitize_html, get_client_ip, get_user_agent
import sqlalchemy as sa
from datetime import datetime

@bp.route('/tickets/<int:ticket_id>/comments', methods=['GET'])
@jwt_required()
def get_ticket_comments(ticket_id):
    """Get all comments for a specific ticket"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if ticket exists
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        # Check if user has access to this ticket
        if not user.is_admin and ticket.created_by_id != user.id and ticket.assigned_to_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get comments based on user permissions
        query = sa.select(TicketComment).where(
            TicketComment.ticket_id == ticket_id,
            TicketComment.is_deleted == False
        ).options(
            sa.orm.joinedload(TicketComment.author)
        ).order_by(TicketComment.created_at.asc())
        
        # Non-admin users can't see internal comments unless they're assigned to the ticket
        if not user.is_admin and ticket.assigned_to_id != user.id:
            query = query.where(TicketComment.is_internal == False)
        
        comments = db.session.scalars(query).all()
        
        comments_data = []
        for comment in comments:
            comment_data = comment.to_dict()
            # Add time ago for better UX
            from app.utils import format_time_ago
            comment_data['time_ago'] = format_time_ago(comment.created_at)
            comments_data.append(comment_data)
        
        return jsonify({
            'comments': comments_data,
            'total': len(comments_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting comments for ticket {ticket_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(ticket_id):
    """Create a new comment on a ticket"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if ticket exists
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        # Check if user has access to this ticket
        if not user.is_admin and ticket.created_by_id != user.id and ticket.assigned_to_id != user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Comment content is required'}), 400
        
        content = data.get('content', '').strip()
        if len(content) < 1:
            return jsonify({'message': 'Comment content cannot be empty'}), 400
        
        if len(content) > 5000:
            return jsonify({'message': 'Comment content is too long (max 5000 characters)'}), 400
        
        # Sanitize HTML content
        sanitized_content = sanitize_html(content)
        
        # Check if this is an internal comment (only admins and assigned users can create internal comments)
        is_internal = data.get('is_internal', False)
        if is_internal and not (user.is_admin or ticket.assigned_to_id == user.id):
            is_internal = False  # Override to false if user doesn't have permission
        
        # Create the comment
        comment = TicketComment(
            content=sanitized_content,
            ticket_id=ticket_id,
            author_id=current_user_id,
            is_internal=is_internal
        )
        
        db.session.add(comment)
        
        # Update ticket's updated_at timestamp
        ticket.updated_at = datetime.utcnow()
        
        # Set first response time if this is the first response from staff
        if not ticket.first_response_at and (user.is_admin or ticket.assigned_to_id == user.id):
            ticket.first_response_at = datetime.utcnow()
            
            # Check if we're within SLA for first response
            if ticket.sla_response_due and ticket.first_response_at <= ticket.sla_response_due:
                # Within SLA, good!
                pass
            elif ticket.sla_response_due and ticket.first_response_at > ticket.sla_response_due:
                # SLA breached
                ticket.sla_response_breached = True
        
        # Create audit log
        audit_log = AuditLog(
            action='COMMENTED',
            details=f"Added comment: {content[:100]}{'...' if len(content) > 100 else ''}",
            user_id=current_user_id,
            ticket_id=ticket_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # Return the created comment
        comment_data = comment.to_dict()
        from app.utils import format_time_ago
        comment_data['time_ago'] = format_time_ago(comment.created_at)
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating comment for ticket {ticket_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update an existing comment"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        comment = db.session.get(TicketComment, comment_id)
        if not comment:
            return jsonify({'message': 'Comment not found'}), 404
        
        # Check if user can edit this comment (author or admin)
        if comment.author_id != current_user_id and not user.is_admin:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Comment content is required'}), 400
        
        content = data.get('content', '').strip()
        if len(content) < 1:
            return jsonify({'message': 'Comment content cannot be empty'}), 400
        
        if len(content) > 5000:
            return jsonify({'message': 'Comment content is too long (max 5000 characters)'}), 400
        
        # Sanitize HTML content
        sanitized_content = sanitize_html(content)
        
        # Update comment
        comment.content = sanitized_content
        comment.updated_at = datetime.utcnow()
        
        # Only allow changing is_internal if user is admin or assigned to ticket
        if 'is_internal' in data and (user.is_admin or comment.ticket.assigned_to_id == current_user_id):
            comment.is_internal = data['is_internal']
        
        # Create audit log
        audit_log = AuditLog(
            action='UPDATED',
            details=f"Updated comment {comment_id}",
            user_id=current_user_id,
            ticket_id=comment.ticket_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        comment_data = comment.to_dict()
        from app.utils import format_time_ago
        comment_data['time_ago'] = format_time_ago(comment.created_at)
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating comment {comment_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Soft delete a comment"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        comment = db.session.get(TicketComment, comment_id)
        if not comment:
            return jsonify({'message': 'Comment not found'}), 404
        
        # Check if user can delete this comment (author or admin)
        if comment.author_id != current_user_id and not user.is_admin:
            return jsonify({'message': 'Access denied'}), 403
        
        # Soft delete the comment
        comment.is_deleted = True
        comment.updated_at = datetime.utcnow()
        
        # Create audit log
        audit_log = AuditLog(
            action='DELETED',
            details=f"Deleted comment {comment_id}",
            user_id=current_user_id,
            ticket_id=comment.ticket_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/comments/<int:comment_id>/restore', methods=['POST'])
@jwt_required()
def restore_comment(comment_id):
    """Restore a soft-deleted comment (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        comment = db.session.get(TicketComment, comment_id)
        if not comment:
            return jsonify({'message': 'Comment not found'}), 404
        
        # Restore the comment
        comment.is_deleted = False
        comment.updated_at = datetime.utcnow()
        
        # Create audit log
        audit_log = AuditLog(
            action='UPDATED',
            details=f"Restored comment {comment_id}",
            user_id=current_user_id,
            ticket_id=comment.ticket_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({'message': 'Comment restored successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restoring comment {comment_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
