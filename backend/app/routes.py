import os
import json
import random
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, send_from_directory
from app import db
from app.forms import (
    LoginForm, TicketForm, EditTicketForm, RegistrationForm,
    ResetPasswordRequestForm, ClientTicketForm, EditProfileForm, ResetPasswordForm
)
import sqlalchemy as sa
from app.models import User, Ticket, ClientTicket
from flask_login import login_required, current_user, logout_user, login_user
from app.email import send_password_reset_email
from urllib.parse import urlsplit
from datetime import datetime
from flask_mail import Message, Mail
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('main', __name__)

class TicketReplyForm(FlaskForm):
    message = TextAreaField('Response', validators=[DataRequired()])
    submit = SubmitField('Send Response')

def get_random_logged_in_user():
    users = db.session.scalars(sa.select(User)).all()
    if not users:
        return None
    return random.choice(users)

# Keep file upload route for serving uploaded files
@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)

# Keep client ticket form (public route, no authentication needed)
@bp.route('/client/ticket/new', methods=['GET', 'POST'])
def client_ticket_new():
    form = ClientTicketForm()
    if form.validate_on_submit():
        # Save uploaded images
        uploaded_filepaths = []
        if form.images.data:
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'client_images')
            os.makedirs(upload_folder, exist_ok=True)

            for file in form.images.data:
                if file:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    uploaded_filepaths.append(f'/static/uploads/client_images/{filename}')

        # Create client ticket
        client_ticket = ClientTicket(
            name=form.name.data,
            surname=form.surname.data,
            phone=form.phone.data,
            email=form.email.data,
            description=form.description.data,
            images=json.dumps(uploaded_filepaths) if uploaded_filepaths else None
        )
        db.session.add(client_ticket)
        db.session.commit()

        # Create internal Ticket linked to client ticket
        assigned_user = get_random_logged_in_user()
        ticket = Ticket(
            title=f"Client Issue from {client_ticket.name} {client_ticket.surname}",
            description=client_ticket.description,
            priority='Medium',
            created_by_id=None,
            assigned_to_id=assigned_user.id if assigned_user else None,
        )
        db.session.add(ticket)
        db.session.commit()

        # Link client_ticket to ticket
        client_ticket.ticket_id = ticket.id
        db.session.commit()

        flash('Your ticket has been submitted successfully. Support will contact you soon.')
        return redirect(url_for('main.client_ticket_new'))

    return render_template('client_ticket_new.html', title='Submit Support Ticket', form=form)

# Keep about page
@bp.route('/about')
def about():
    return render_template('about.html', title='About')

# Keep email preview routes if needed for development
@bp.route('/email-preview/<template_name>')
def preview_email_template(template_name):
    """Preview email templates for development"""
    return render_template(f'email/{template_name}.html')