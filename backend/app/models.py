from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from time import time
import jwt
from datetime import datetime
from flask import current_app

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'about_me': self.about_me if hasattr(self, 'about_me') else '',
            'last_seen': self.last_seen.isoformat() if hasattr(self, 'last_seen') and self.last_seen else None,
            'is_admin': self.is_admin
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


class Ticket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    status: so.Mapped[str] = so.mapped_column(sa.String(50), default='Open')
    priority: so.Mapped[str] = so.mapped_column(sa.String(50), default="Medium")
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    created_by: so.Mapped["User"] = so.relationship(
        "User", foreign_keys=[created_by_id], backref="tickets"
    )

    assigned_to_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    assigned_to: so.Mapped[Optional["User"]] = so.relationship(
        "User", foreign_keys=[assigned_to_id], backref="assigned_tickets"
    )

    client_ticket: so.Mapped[Optional["ClientTicket"]] = so.relationship(
        "ClientTicket", back_populates="ticket", uselist=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority if hasattr(self, 'priority') else 'Medium',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by_id': self.created_by_id,
            'assigned_to_id': self.assigned_to_id
        }

    def __repr__(self):
        return f"<Ticket {self.id} - {self.title} ({self.status})>"


class ClientTicket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    surname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    phone: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    images: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    ticket_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('ticket.id'))
    ticket: so.Mapped[Optional["Ticket"]] = so.relationship(
        "Ticket", back_populates="client_ticket"
    )


class TokenBlacklist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    jti: so.Mapped[str] = so.mapped_column(sa.String(36), nullable=False, unique=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
