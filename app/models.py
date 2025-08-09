from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from time import time
import jwt
from app import app
from datetime import datetime

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
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
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    created_by_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    created_by: so.Mapped["User"] = so.relationship(
        "User", foreign_keys=[created_by_id], backref="tickets"
    )

    assigned_to_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)
    assigned_to: so.Mapped[Optional["User"]] = so.relationship(
        "User", foreign_keys=[assigned_to_id], backref="assigned_tickets"
    )

    def __repr__(self):
        return f"<Ticket {self.id} - {self.title} ({self.status})>"