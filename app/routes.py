from flask import render_template
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/tickets') #placeholder for now
def tickets():
    return render_template('tickets.html', title='Tickets')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me{}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)