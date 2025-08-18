from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from time import time
import jwt
from datetime import datetime, timedelta
from flask import current_app
import enum

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Enums for better data integrity
class TicketStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"

class TicketPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class SLAStatus(enum.Enum):
    WITHIN_SLA = "Within SLA"
    APPROACHING_BREACH = "Approaching Breach"
    BREACHED = "Breached"

class AuditAction(enum.Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    DELETED = "Deleted"
    ASSIGNED = "Assigned"
    COMMENTED = "Commented"
    STATUS_CHANGED = "Status Changed"
    PRIORITY_CHANGED = "Priority Changed"

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    
    # New fields for enhanced functionality
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    department: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    job_title: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    timezone: so.Mapped[str] = so.mapped_column(sa.String(50), default='UTC')
    email_notifications: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    
    # Relationships
    created_tickets: so.Mapped[list["Ticket"]] = so.relationship(
        "Ticket", foreign_keys="Ticket.created_by_id", back_populates="created_by"
    )
    assigned_tickets: so.Mapped[list["Ticket"]] = so.relationship(
        "Ticket", foreign_keys="Ticket.assigned_to_id", back_populates="assigned_to"
    )
    comments: so.Mapped[list["TicketComment"]] = so.relationship(
        "TicketComment", back_populates="author", cascade="all, delete-orphan"
    )
    audit_logs: so.Mapped[list["AuditLog"]] = so.relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'about_me': self.about_me if hasattr(self, 'about_me') else '',
            'last_seen': self.last_seen.isoformat() if hasattr(self, 'last_seen') and self.last_seen else None,
            'is_admin': self.is_admin,
            'is_active': getattr(self, 'is_active', True),
            'phone': getattr(self, 'phone', ''),
            'department': getattr(self, 'department', ''),
            'job_title': getattr(self, 'job_title', ''),
            'timezone': getattr(self, 'timezone', 'UTC'),
            'email_notifications': getattr(self, 'email_notifications', True)
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)


class TicketCategory(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False, unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    color: so.Mapped[str] = so.mapped_column(sa.String(7), default='#3B82F6')  # Hex color
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    
    # SLA settings for this category
    sla_response_hours: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, default=24)
    sla_resolution_hours: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, default=72)
    
    # Relationships
    tickets: so.Mapped[list["Ticket"]] = so.relationship(
        "Ticket", back_populates="category"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'is_active': self.is_active,
            'sla_response_hours': self.sla_response_hours,
            'sla_resolution_hours': self.sla_resolution_hours,
            'ticket_count': len(self.tickets) if self.tickets else 0
        }


class Ticket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False, index=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    status: so.Mapped[str] = so.mapped_column(sa.String(50), default='Open', index=True)
    priority: so.Mapped[str] = so.mapped_column(sa.String(50), default="Medium", index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Enhanced fields
    ticket_number: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True, index=True)
    is_deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, index=True)  # Soft delete
    resolution_notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    resolved_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
    closed_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
    
    # Time tracking
    estimated_hours: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    actual_hours: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    
    # SLA tracking
    sla_response_due: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, index=True)
    sla_resolution_due: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, index=True)
    sla_response_breached: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    sla_resolution_breached: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    first_response_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)

    # Foreign keys
    created_by_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True, index=True)
    assigned_to_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True, index=True)
    category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('ticket_category.id'), nullable=True, index=True)

    # Relationships
    created_by: so.Mapped[Optional["User"]] = so.relationship(
        "User", foreign_keys=[created_by_id], back_populates="created_tickets"
    )
    assigned_to: so.Mapped[Optional["User"]] = so.relationship(
        "User", foreign_keys=[assigned_to_id], back_populates="assigned_tickets"
    )
    category: so.Mapped[Optional["TicketCategory"]] = so.relationship(
        "TicketCategory", back_populates="tickets"
    )
    client_ticket: so.Mapped[Optional["ClientTicket"]] = so.relationship(
        "ClientTicket", back_populates="ticket", uselist=False
    )
    comments: so.Mapped[list["TicketComment"]] = so.relationship(
        "TicketComment", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketComment.created_at"
    )
    attachments: so.Mapped[list["TicketAttachment"]] = so.relationship(
        "TicketAttachment", back_populates="ticket", cascade="all, delete-orphan"
    )
    watchers: so.Mapped[list["TicketWatcher"]] = so.relationship(
        "TicketWatcher", back_populates="ticket", cascade="all, delete-orphan"
    )
    audit_logs: so.Mapped[list["AuditLog"]] = so.relationship(
        "AuditLog", back_populates="ticket", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        self.calculate_sla_dates()

    def generate_ticket_number(self):
        """Generate a unique ticket number"""
        import random
        import string
        prefix = "TKT"
        timestamp = int(datetime.utcnow().timestamp())
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}-{timestamp}-{random_suffix}"

    def calculate_sla_dates(self):
        """Calculate SLA due dates based on category settings"""
        if self.category and self.created_at:
            if self.category.sla_response_hours:
                self.sla_response_due = self.created_at + timedelta(hours=self.category.sla_response_hours)
            if self.category.sla_resolution_hours:
                self.sla_resolution_due = self.created_at + timedelta(hours=self.category.sla_resolution_hours)

    def get_sla_status(self):
        """Get current SLA status"""
        now = datetime.utcnow()
        
        if self.sla_resolution_breached or (self.sla_resolution_due and now > self.sla_resolution_due):
            return SLAStatus.BREACHED
        elif self.sla_resolution_due:
            hours_until_breach = (self.sla_resolution_due - now).total_seconds() / 3600
            if hours_until_breach <= 4:  # 4 hours warning
                return SLAStatus.APPROACHING_BREACH
        
        return SLAStatus.WITHIN_SLA

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_number': getattr(self, 'ticket_number', f'TKT-{self.id}'),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if getattr(self, 'resolved_at', None) else None,
            'closed_at': self.closed_at.isoformat() if getattr(self, 'closed_at', None) else None,
            'created_by_id': self.created_by_id,
            'assigned_to_id': self.assigned_to_id,
            'category_id': getattr(self, 'category_id', None),
            'estimated_hours': getattr(self, 'estimated_hours', None),
            'actual_hours': getattr(self, 'actual_hours', None),
            'sla_status': self.get_sla_status().value if hasattr(self, 'get_sla_status') else 'Within SLA',
            'comment_count': len(getattr(self, 'comments', [])),
            'attachment_count': len(getattr(self, 'attachments', []))
        }

    def __repr__(self):
        ticket_num = getattr(self, 'ticket_number', f'TKT-{self.id}')
        return f"<Ticket {ticket_num} - {self.title} ({self.status})>"


class TicketComment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    updated_at: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime, onupdate=datetime.utcnow)
    is_internal: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)  # Internal notes vs client-visible
    is_deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    
    # Foreign keys
    ticket_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('ticket.id'), nullable=False, index=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False, index=True)
    
    # Relationships
    ticket: so.Mapped["Ticket"] = so.relationship("Ticket", back_populates="comments")
    author: so.Mapped["User"] = so.relationship("User", back_populates="comments")

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_internal': self.is_internal,
            'ticket_id': self.ticket_id,
            'author': {
                'id': self.author.id,
                'username': self.author.username
            } if self.author else None
        }


class TicketAttachment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    original_filename: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    file_size: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    mime_type: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    file_path: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=False)
    uploaded_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    ticket_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('ticket.id'), nullable=False, index=True)
    uploaded_by_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    ticket: so.Mapped["Ticket"] = so.relationship("Ticket", back_populates="attachments")
    uploaded_by: so.Mapped["User"] = so.relationship("User")

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_at': self.uploaded_at.isoformat(),
            'uploaded_by': {
                'id': self.uploaded_by.id,
                'username': self.uploaded_by.username
            } if self.uploaded_by else None
        }


class TicketWatcher(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    ticket_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('ticket.id'), nullable=False, index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False, index=True)
    
    # Relationships
    ticket: so.Mapped["Ticket"] = so.relationship("Ticket", back_populates="watchers")
    user: so.Mapped["User"] = so.relationship("User")
    
    # Unique constraint
    __table_args__ = (sa.UniqueConstraint('ticket_id', 'user_id'),)


class ClientTicket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    surname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    phone: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False, index=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    images: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    
    # Enhanced fields
    company: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    reference_number: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True, index=True)

    ticket_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('ticket.id'))
    ticket: so.Mapped[Optional["Ticket"]] = so.relationship(
        "Ticket", back_populates="client_ticket"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.reference_number:
            self.reference_number = f"CT{self.id:06d}" if self.id else None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'phone': self.phone,
            'email': self.email,
            'company': getattr(self, 'company', ''),
            'description': self.description,
            'reference_number': getattr(self, 'reference_number', f"CT{self.id:06d}"),
            'created_at': self.created_at.isoformat(),
            'images': self.images,
            'ticket_id': self.ticket_id
        }


class AuditLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    action: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False, index=True)
    details: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)
    ip_address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(45))
    user_agent: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    
    # Foreign keys
    user_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True, index=True)
    ticket_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('ticket.id'), nullable=True, index=True)
    
    # Relationships
    user: so.Mapped[Optional["User"]] = so.relationship("User", back_populates="audit_logs")
    ticket: so.Mapped[Optional["Ticket"]] = so.relationship("Ticket", back_populates="audit_logs")

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'ip_address': self.ip_address,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None,
            'ticket_id': self.ticket_id
        }


class TokenBlacklist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    jti: so.Mapped[str] = so.mapped_column(sa.String(36), nullable=False, unique=True, index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow, index=True)


# Create database indexes for performance
def create_indexes():
    """Create additional database indexes for performance"""
    try:
        # Ticket indexes
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_ticket_status_priority ON ticket(status, priority)'))
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_ticket_created_assigned ON ticket(created_by_id, assigned_to_id)'))
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_ticket_sla_dates ON ticket(sla_response_due, sla_resolution_due)'))
        
        # Comment indexes
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_comment_ticket_created ON ticket_comment(ticket_id, created_at)'))
        
        # Audit log indexes
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_audit_user_created ON audit_log(user_id, created_at)'))
        db.engine.execute(sa.text('CREATE INDEX IF NOT EXISTS idx_audit_ticket_created ON audit_log(ticket_id, created_at)'))
        
    except Exception as e:
        print(f"Error creating indexes: {e}")
