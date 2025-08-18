from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, TicketCategory, Ticket, AuditLog
from app import db
from app.utils import sanitize_html, get_client_ip, get_user_agent
import sqlalchemy as sa
from datetime import datetime
import re

@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all ticket categories"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get all active categories with ticket counts
        query = sa.select(TicketCategory).where(
            TicketCategory.is_active == True
        ).order_by(TicketCategory.name)
        
        categories = db.session.scalars(query).all()
        
        categories_data = []
        for category in categories:
            category_data = category.to_dict()
            
            # Add ticket counts by status
            ticket_counts = db.session.execute(
                sa.select(
                    Ticket.status,
                    sa.func.count(Ticket.id).label('count')
                ).where(
                    Ticket.category_id == category.id,
                    Ticket.is_deleted == False
                ).group_by(Ticket.status)
            ).all()
            
            status_counts = {row.status: row.count for row in ticket_counts}
            category_data['ticket_counts'] = {
                'total': sum(status_counts.values()),
                'open': status_counts.get('Open', 0),
                'in_progress': status_counts.get('In Progress', 0),
                'resolved': status_counts.get('Resolved', 0),
                'closed': status_counts.get('Closed', 0)
            }
            
            categories_data.append(category_data)
        
        return jsonify({
            'categories': categories_data,
            'total': len(categories_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new ticket category (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request data is required'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'message': 'Category name is required'}), 400
        
        if len(name) < 2:
            return jsonify({'message': 'Category name must be at least 2 characters long'}), 400
        
        if len(name) > 100:
            return jsonify({'message': 'Category name must be less than 100 characters'}), 400
        
        # Check if category name already exists
        existing = db.session.scalar(
            sa.select(TicketCategory).where(TicketCategory.name == name)
        )
        if existing:
            return jsonify({'message': 'Category with this name already exists'}), 400
        
        description = data.get('description', '').strip()
        if description:
            description = sanitize_html(description)
            if len(description) > 1000:
                return jsonify({'message': 'Description must be less than 1000 characters'}), 400
        
        # Validate color (hex color format)
        color = data.get('color', '#3B82F6').strip()
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            color = '#3B82F6'  # Default color
        
        # Validate SLA hours
        sla_response_hours = data.get('sla_response_hours')
        sla_resolution_hours = data.get('sla_resolution_hours')
        
        if sla_response_hours is not None:
            try:
                sla_response_hours = int(sla_response_hours)
                if sla_response_hours < 1 or sla_response_hours > 8760:  # Max 1 year
                    return jsonify({'message': 'SLA response hours must be between 1 and 8760'}), 400
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid SLA response hours'}), 400
        
        if sla_resolution_hours is not None:
            try:
                sla_resolution_hours = int(sla_resolution_hours)
                if sla_resolution_hours < 1 or sla_resolution_hours > 8760:  # Max 1 year
                    return jsonify({'message': 'SLA resolution hours must be between 1 and 8760'}), 400
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid SLA resolution hours'}), 400
        
        # Create category
        category = TicketCategory(
            name=name,
            description=description or None,
            color=color,
            sla_response_hours=sla_response_hours or 24,
            sla_resolution_hours=sla_resolution_hours or 72,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        
        # Create audit log
        audit_log = AuditLog(
            action='CREATED',
            details=f"Created category: {name}",
            user_id=current_user_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating category: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Get a specific category with detailed information"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        category = db.session.get(TicketCategory, category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        category_data = category.to_dict()
        
        # Add detailed ticket statistics
        ticket_stats = db.session.execute(
            sa.select(
                Ticket.status,
                Ticket.priority,
                sa.func.count(Ticket.id).label('count')
            ).where(
                Ticket.category_id == category_id,
                Ticket.is_deleted == False
            ).group_by(Ticket.status, Ticket.priority)
        ).all()
        
        # Organize stats
        status_counts = {}
        priority_counts = {}
        
        for stat in ticket_stats:
            # Status counts
            if stat.status not in status_counts:
                status_counts[stat.status] = 0
            status_counts[stat.status] += stat.count
            
            # Priority counts
            if stat.priority not in priority_counts:
                priority_counts[stat.priority] = 0
            priority_counts[stat.priority] += stat.count
        
        category_data['detailed_stats'] = {
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'total_tickets': sum(status_counts.values())
        }
        
        # Get recent tickets in this category
        recent_tickets = db.session.scalars(
            sa.select(Ticket).where(
                Ticket.category_id == category_id,
                Ticket.is_deleted == False
            ).options(
                sa.orm.joinedload(Ticket.created_by),
                sa.orm.joinedload(Ticket.assigned_to)
            ).order_by(Ticket.created_at.desc()).limit(5)
        ).all()
        
        category_data['recent_tickets'] = [
            {
                'id': ticket.id,
                'title': ticket.title,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat(),
                'created_by': ticket.created_by.username if ticket.created_by else 'Client'
            }
            for ticket in recent_tickets
        ]
        
        return jsonify(category_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting category {category_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update a category (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        category = db.session.get(TicketCategory, category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request data is required'}), 400
        
        # Update name if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'message': 'Category name cannot be empty'}), 400
            
            if len(name) < 2:
                return jsonify({'message': 'Category name must be at least 2 characters long'}), 400
            
            if len(name) > 100:
                return jsonify({'message': 'Category name must be less than 100 characters'}), 400
            
            # Check if name already exists (excluding current category)
            existing = db.session.scalar(
                sa.select(TicketCategory).where(
                    TicketCategory.name == name,
                    TicketCategory.id != category_id
                )
            )
            if existing:
                return jsonify({'message': 'Category with this name already exists'}), 400
            
            category.name = name
        
        # Update description if provided
        if 'description' in data:
            description = data['description'].strip() if data['description'] else ''
            if description:
                description = sanitize_html(description)
                if len(description) > 1000:
                    return jsonify({'message': 'Description must be less than 1000 characters'}), 400
            category.description = description or None
        
        # Update color if provided
        if 'color' in data:
            color = data['color'].strip()
            if re.match(r'^#[0-9A-Fa-f]{6}$', color):
                category.color = color
        
        # Update SLA settings if provided
        if 'sla_response_hours' in data:
            try:
                sla_response_hours = int(data['sla_response_hours'])
                if 1 <= sla_response_hours <= 8760:
                    category.sla_response_hours = sla_response_hours
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid SLA response hours'}), 400
        
        if 'sla_resolution_hours' in data:
            try:
                sla_resolution_hours = int(data['sla_resolution_hours'])
                if 1 <= sla_resolution_hours <= 8760:
                    category.sla_resolution_hours = sla_resolution_hours
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid SLA resolution hours'}), 400
        
        # Update active status if provided
        if 'is_active' in data:
            category.is_active = bool(data['is_active'])
        
        # Create audit log
        audit_log = AuditLog(
            action='UPDATED',
            details=f"Updated category: {category.name}",
            user_id=current_user_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating category {category_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Deactivate a category (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        category = db.session.get(TicketCategory, category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        
        # Check if category has active tickets
        active_ticket_count = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.category_id == category_id,
                Ticket.is_deleted == False,
                Ticket.status.in_(['Open', 'In Progress', 'Pending'])
            )
        )
        
        if active_ticket_count > 0:
            return jsonify({
                'message': f'Cannot delete category with {active_ticket_count} active tickets. Please reassign or close them first.'
            }), 400
        
        # Soft delete by deactivating
        category.is_active = False
        
        # Create audit log
        audit_log = AuditLog(
            action='DELETED',
            details=f"Deactivated category: {category.name}",
            user_id=current_user_id,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({'message': 'Category deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting category {category_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
