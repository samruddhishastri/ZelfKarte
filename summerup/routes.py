from flask import render_template, url_for, flash, redirect
from summerup import app
from summerup.models import User
from summerup.forms import SignupForm, LoginForm

@app.route("/")
def launch():
	return render_template('launching_page.html')

@app.route("/xyz")
def home():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('home'))
	return render_template('signup.html', title='Signup', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == 'admin@blog.com' and form.password.data == 'password':
			flash('You have been logged in!', 'success')
			return redirect(url_for('home'))
		else:
			flash('Login failed. Please recheck your email and password.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/qrcode')
def qrcode():
	return render_template('qrcode.html', title='Scan')