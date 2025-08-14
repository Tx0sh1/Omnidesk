import os
import random
import sqlalchemy as sa
from flask import Blueprint, render_template, current_app, send_from_directory
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from app import db
from app.models import User

bp = Blueprint('main', __name__)

# --- Forms ---
class TicketReplyForm(FlaskForm):
    message = TextAreaField('Response', validators=[DataRequired()])
    submit = SubmitField('Send Response')

# --- Utility functions ---
def get_random_logged_in_user():
    users = db.session.scalars(sa.select(User)).all()
    if not users:
        return None
    return random.choice(users)

# --- Routes ---
@bp.route('/')
def index():
    """Serve the static index page"""
    return send_from_directory(current_app.static_folder, 'index.html')


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)


@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html', title='About')


@bp.route('/email-preview/<template_name>')
def preview_email_template(template_name):
    """Preview email templates for development"""
    return render_template(f'email/{template_name}.html')
