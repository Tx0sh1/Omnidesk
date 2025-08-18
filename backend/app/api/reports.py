from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, Ticket, TicketCategory, TicketComment, AuditLog, ClientTicket
from app import db
from app.utils import paginate_query
import sqlalchemy as sa
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

@bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics and metrics"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Date range filter (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic ticket counts
        total_tickets = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(Ticket.is_deleted == False)
        )
        
        open_tickets = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                Ticket.status == 'Open'
            )
        )
        
        in_progress_tickets = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                Ticket.status == 'In Progress'
            )
        )
        
        resolved_tickets = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                Ticket.status.in_(['Resolved', 'Closed'])
            )
        )
        
        # Recent activity (tickets created in date range)
        recent_tickets = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                Ticket.created_at >= start_date
            )
        )
        
        # SLA metrics
        sla_breached = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                sa.or_(
                    Ticket.sla_response_breached == True,
                    Ticket.sla_resolution_breached == True
                )
            )
        )
        
        approaching_sla = db.session.scalar(
            sa.select(sa.func.count(Ticket.id)).where(
                Ticket.is_deleted == False,
                Ticket.status.in_(['Open', 'In Progress']),
                sa.or_(
                    Ticket.sla_response_due <= datetime.utcnow() + timedelta(hours=4),
                    Ticket.sla_resolution_due <= datetime.utcnow() + timedelta(hours=4)
                )
            )
        )
        
        # User metrics
        total_users = db.session.scalar(
            sa.select(sa.func.count(User.id)).where(User.is_active == True)
        )
        
        active_users = db.session.scalar(
            sa.select(sa.func.count(User.id)).where(
                User.is_active == True,
                User.last_seen >= start_date
            )
        )
        
        # Category distribution
        category_stats = db.session.execute(
            sa.select(
                TicketCategory.name,
                TicketCategory.color,
                sa.func.count(Ticket.id).label('count')
            ).select_from(
                TicketCategory
            ).outerjoin(
                Ticket, sa.and_(
                    Ticket.category_id == TicketCategory.id,
                    Ticket.is_deleted == False
                )
            ).where(
                TicketCategory.is_active == True
            ).group_by(TicketCategory.id, TicketCategory.name, TicketCategory.color)
        ).all()
        
        # Priority distribution
        priority_stats = db.session.execute(
            sa.select(
                Ticket.priority,
                sa.func.count(Ticket.id).label('count')
            ).where(
                Ticket.is_deleted == False
            ).group_by(Ticket.priority)
        ).all()
        
        # Recent comments count
        recent_comments = db.session.scalar(
            sa.select(sa.func.count(TicketComment.id)).where(
                TicketComment.is_deleted == False,
                TicketComment.created_at >= start_date
            )
        )
        
        # Compile dashboard data
        dashboard_data = {
            'overview': {
                'total_tickets': total_tickets,
                'open_tickets': open_tickets,
                'in_progress_tickets': in_progress_tickets,
                'resolved_tickets': resolved_tickets,
                'recent_tickets': recent_tickets,
                'resolution_rate': round((resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0, 1)
            },
            'sla_metrics': {
                'breached': sla_breached,
                'approaching': approaching_sla,
                'compliance_rate': round(((total_tickets - sla_breached) / total_tickets * 100) if total_tickets > 0 else 100, 1)
            },
            'user_metrics': {
                'total_users': total_users,
                'active_users': active_users,
                'activity_rate': round((active_users / total_users * 100) if total_users > 0 else 0, 1)
            },
            'category_distribution': [
                {
                    'name': stat.name,
                    'color': stat.color,
                    'count': stat.count,
                    'percentage': round((stat.count / total_tickets * 100) if total_tickets > 0 else 0, 1)
                }
                for stat in category_stats
            ],
            'priority_distribution': [
                {
                    'priority': stat.priority,
                    'count': stat.count,
                    'percentage': round((stat.count / total_tickets * 100) if total_tickets > 0 else 0, 1)
                }
                for stat in priority_stats
            ],
            'activity': {
                'recent_comments': recent_comments,
                'date_range_days': days
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating dashboard stats: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/reports/trends', methods=['GET'])
@jwt_required()
def get_trends():
    """Get trend data for charts"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily ticket creation trend
        daily_tickets = db.session.execute(
            sa.select(
                sa.func.date(Ticket.created_at).label('date'),
                sa.func.count(Ticket.id).label('count')
            ).where(
                Ticket.is_deleted == False,
                Ticket.created_at >= start_date
            ).group_by(sa.func.date(Ticket.created_at))
            .order_by(sa.func.date(Ticket.created_at))
        ).all()
        
        # Daily resolution trend
        daily_resolutions = db.session.execute(
            sa.select(
                sa.func.date(Ticket.resolved_at).label('date'),
                sa.func.count(Ticket.id).label('count')
            ).where(
                Ticket.is_deleted == False,
                Ticket.resolved_at >= start_date,
                Ticket.resolved_at.is_not(None)
            ).group_by(sa.func.date(Ticket.resolved_at))
            .order_by(sa.func.date(Ticket.resolved_at))
        ).all()
        
        # Status changes over time
        status_trends = db.session.execute(
            sa.select(
                sa.func.date(Ticket.updated_at).label('date'),
                Ticket.status,
                sa.func.count(Ticket.id).label('count')
            ).where(
                Ticket.is_deleted == False,
                Ticket.updated_at >= start_date
            ).group_by(sa.func.date(Ticket.updated_at), Ticket.status)
            .order_by(sa.func.date(Ticket.updated_at))
        ).all()
        
        # Response time trends (average first response time by day)
        response_times = db.session.execute(
            sa.select(
                sa.func.date(Ticket.created_at).label('date'),
                sa.func.avg(
                    sa.extract('epoch', Ticket.first_response_at - Ticket.created_at) / 3600
                ).label('avg_response_hours')
            ).where(
                Ticket.is_deleted == False,
                Ticket.created_at >= start_date,
                Ticket.first_response_at.is_not(None)
            ).group_by(sa.func.date(Ticket.created_at))
            .order_by(sa.func.date(Ticket.created_at))
        ).all()
        
        # Format trend data
        trends_data = {
            'daily_tickets': [
                {
                    'date': row.date.isoformat(),
                    'count': row.count
                }
                for row in daily_tickets
            ],
            'daily_resolutions': [
                {
                    'date': row.date.isoformat(),
                    'count': row.count
                }
                for row in daily_resolutions
            ],
            'status_trends': {},
            'response_times': [
                {
                    'date': row.date.isoformat(),
                    'avg_hours': round(float(row.avg_response_hours), 2) if row.avg_response_hours else 0
                }
                for row in response_times
            ]
        }
        
        # Group status trends by status
        for row in status_trends:
            status = row.status
            if status not in trends_data['status_trends']:
                trends_data['status_trends'][status] = []
            
            trends_data['status_trends'][status].append({
                'date': row.date.isoformat(),
                'count': row.count
            })
        
        return jsonify(trends_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating trends: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/reports/performance', methods=['GET'])
@jwt_required()
def get_performance_metrics():
    """Get performance metrics and KPIs"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Date range
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Average resolution time
        avg_resolution_time = db.session.scalar(
            sa.select(
                sa.func.avg(
                    sa.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600
                )
            ).where(
                Ticket.is_deleted == False,
                Ticket.resolved_at.is_not(None),
                Ticket.created_at >= start_date
            )
        )
        
        # Average first response time
        avg_response_time = db.session.scalar(
            sa.select(
                sa.func.avg(
                    sa.extract('epoch', Ticket.first_response_at - Ticket.created_at) / 3600
                )
            ).where(
                Ticket.is_deleted == False,
                Ticket.first_response_at.is_not(None),
                Ticket.created_at >= start_date
            )
        )
        
        # Agent performance (tickets resolved per agent)
        agent_performance = db.session.execute(
            sa.select(
                User.username,
                sa.func.count(Ticket.id).label('resolved_tickets'),
                sa.func.avg(
                    sa.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600
                ).label('avg_resolution_hours')
            ).select_from(User).join(
                Ticket, Ticket.assigned_to_id == User.id
            ).where(
                Ticket.is_deleted == False,
                Ticket.resolved_at.is_not(None),
                Ticket.resolved_at >= start_date
            ).group_by(User.id, User.username)
            .order_by(sa.func.count(Ticket.id).desc())
        ).all()
        
        # Category performance
        category_performance = db.session.execute(
            sa.select(
                TicketCategory.name,
                sa.func.count(Ticket.id).label('total_tickets'),
                sa.func.sum(
                    sa.case((Ticket.status.in_(['Resolved', 'Closed']), 1), else_=0)
                ).label('resolved_tickets'),
                sa.func.avg(
                    sa.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600
                ).label('avg_resolution_hours')
            ).select_from(TicketCategory).join(
                Ticket, Ticket.category_id == TicketCategory.id
            ).where(
                Ticket.is_deleted == False,
                Ticket.created_at >= start_date
            ).group_by(TicketCategory.id, TicketCategory.name)
        ).all()
        
        # SLA compliance by category
        sla_compliance = db.session.execute(
            sa.select(
                TicketCategory.name,
                sa.func.count(Ticket.id).label('total_tickets'),
                sa.func.sum(
                    sa.case((Ticket.sla_response_breached == False, 1), else_=0)
                ).label('response_within_sla'),
                sa.func.sum(
                    sa.case((Ticket.sla_resolution_breached == False, 1), else_=0)
                ).label('resolution_within_sla')
            ).select_from(TicketCategory).join(
                Ticket, Ticket.category_id == TicketCategory.id
            ).where(
                Ticket.is_deleted == False,
                Ticket.created_at >= start_date
            ).group_by(TicketCategory.id, TicketCategory.name)
        ).all()
        
        performance_data = {
            'overall_metrics': {
                'avg_resolution_hours': round(float(avg_resolution_time), 2) if avg_resolution_time else 0,
                'avg_response_hours': round(float(avg_response_time), 2) if avg_response_time else 0,
                'date_range_days': days
            },
            'agent_performance': [
                {
                    'username': row.username,
                    'resolved_tickets': row.resolved_tickets,
                    'avg_resolution_hours': round(float(row.avg_resolution_hours), 2) if row.avg_resolution_hours else 0
                }
                for row in agent_performance
            ],
            'category_performance': [
                {
                    'category': row.name,
                    'total_tickets': row.total_tickets,
                    'resolved_tickets': row.resolved_tickets,
                    'resolution_rate': round((row.resolved_tickets / row.total_tickets * 100) if row.total_tickets > 0 else 0, 1),
                    'avg_resolution_hours': round(float(row.avg_resolution_hours), 2) if row.avg_resolution_hours else 0
                }
                for row in category_performance
            ],
            'sla_compliance': [
                {
                    'category': row.name,
                    'total_tickets': row.total_tickets,
                    'response_compliance': round((row.response_within_sla / row.total_tickets * 100) if row.total_tickets > 0 else 0, 1),
                    'resolution_compliance': round((row.resolution_within_sla / row.total_tickets * 100) if row.total_tickets > 0 else 0, 1)
                }
                for row in sla_compliance
            ]
        }
        
        return jsonify(performance_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating performance metrics: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@bp.route('/reports/export', methods=['GET'])
@jwt_required()
def export_report():
    """Export report data (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        report_type = request.args.get('type', 'tickets')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.utcnow() - timedelta(days=30)
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.utcnow()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        if report_type == 'tickets':
            # Export ticket data
            tickets = db.session.scalars(
                sa.select(Ticket).where(
                    Ticket.is_deleted == False,
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                ).options(
                    sa.orm.joinedload(Ticket.created_by),
                    sa.orm.joinedload(Ticket.assigned_to),
                    sa.orm.joinedload(Ticket.category)
                ).order_by(Ticket.created_at.desc())
            ).all()
            
            export_data = [
                {
                    'id': ticket.id,
                    'ticket_number': getattr(ticket, 'ticket_number', f'TKT-{ticket.id}'),
                    'title': ticket.title,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'category': ticket.category.name if ticket.category else 'Uncategorized',
                    'created_by': ticket.created_by.username if ticket.created_by else 'Client',
                    'assigned_to': ticket.assigned_to.username if ticket.assigned_to else 'Unassigned',
                    'created_at': ticket.created_at.isoformat(),
                    'resolved_at': ticket.resolved_at.isoformat() if getattr(ticket, 'resolved_at', None) else None,
                    'sla_breached': getattr(ticket, 'sla_resolution_breached', False)
                }
                for ticket in tickets
            ]
            
        elif report_type == 'audit':
            # Export audit log data
            audit_logs = db.session.scalars(
                sa.select(AuditLog).where(
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date
                ).options(
                    sa.orm.joinedload(AuditLog.user)
                ).order_by(AuditLog.created_at.desc())
            ).all()
            
            export_data = [
                {
                    'id': log.id,
                    'action': log.action,
                    'details': log.details,
                    'user': log.user.username if log.user else 'System',
                    'ticket_id': log.ticket_id,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at.isoformat()
                }
                for log in audit_logs
            ]
            
        else:
            return jsonify({'message': 'Invalid report type'}), 400
        
        return jsonify({
            'report_type': report_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_records': len(export_data),
            'data': export_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error exporting report: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
