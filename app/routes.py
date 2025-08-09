from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, TicketForm, EditTicketForm, RegistrationForm, ResetPasswordRequestForm
import sqlalchemy as sa
from app.models import User, Ticket
from flask_login import login_required, current_user, logout_user, login_user
from app.email import send_password_reset_email
from urllib.parse import urlsplit
from datetime import datetime



@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

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

@app.route('/tickets/new', methods=['Get', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))