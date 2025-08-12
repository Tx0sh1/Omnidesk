import os
import json
import random
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, current_app
from app import app, db, email
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
from flask_mail import Message
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired



@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

class TicketReplyForm(FlaskForm):
    message = TextAreaField('Response', validators=[DataRequired()])
    submit = SubmitField('Send Response')

# -- Utility: Pick random logged-in user (simple version) --
def get_random_logged_in_user():
    users = db.session.scalars(sa.select(User)).all()
    if not users:
        return None
    return random.choice(users)


@app.route('/tickets/<int:ticket_id>/reply', methods=['GET', 'POST'])
@login_required
def reply_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        flash('Ticket not found.')
        return redirect(url_for('tickets'))

    form = TicketReplyForm()
    if form.validate_on_submit():
        # Here you can implement saving the reply to DB if you want (not shown)

        # Send email to client if email exists
        if ticket.client_ticket and ticket.client_ticket.email:
            msg = Message(
                subject=f"Response to your support ticket #{ticket.id}",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[ticket.client_ticket.email]
            )
            msg.body = (
                f"Dear {ticket.client_ticket.name},\n\n"
                f"{form.message.data}\n\n"
                "Best regards,\nSupport Team"
            )
            mail.send(msg)

        flash('Response sent to client via email.')
        return redirect(url_for('edit_ticket', ticket_id=ticket_id))

    return render_template('reply_ticket.html', title='Reply to Ticket', form=form, ticket=ticket)

@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = getattr(current_user, 'about_me', '')  # fallback if missing
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/tickets')
@login_required
def tickets():
    all_tickets = db.session.scalars(sa.select(Ticket)).all()
    return render_template('tickets.html', title='Tickets', tickets=all_tickets)

@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            created_by=current_user
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully')
        return redirect(url_for('tickets'))
    return render_template('new_ticket.html', title='New Ticket', form=form)

@app.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        flash('Ticket not found.')
        return redirect(url_for('tickets'))

    form = EditTicketForm(obj=ticket)
    
    
    users = db.session.scalars(sa.select(User)).all()
    form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.description = form.description.data
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        ticket.assigned_to_id = form.assigned_to.data if form.assigned_to.data != 0 else None
        db.session.commit()
        flash('Ticket updated successfully.')
        return redirect(url_for('tickets'))

    
    form.assigned_to.data = ticket.assigned_to_id if ticket.assigned_to_id else 0
    return render_template('edit_ticket.html', title='Edit Ticket', form=form, ticket=ticket)

@app.route('/client/ticket/new', methods=['GET', 'POST'])
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
            priority='Medium',  # default, can be updated by staff later
            created_by_id=None,  # or set to a system user if you have one
            assigned_to_id=assigned_user.id if assigned_user else None,
        )
        db.session.add(ticket)
        db.session.commit()

        # Link client_ticket to ticket
        client_ticket.ticket_id = ticket.id
        db.session.commit()

        flash('Your ticket has been submitted successfully. Support will contact you soon.')
        return redirect(url_for('client_ticket_new'))

    return render_template('client_ticket_new.html', title='Submit Support Ticket', form=form)


@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)       
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
