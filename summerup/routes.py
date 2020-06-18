from flask import render_template, url_for, flash, redirect, request
from summerup import app, db, bcrypt
from summerup.models import User
from summerup.forms import SignupForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def launch():
	return render_template('launching_page.html')

@app.route("/home")
@login_required
def home():
	return render_template('home.html')

@app.route('/about')
@login_required
def about():
	return render_template('about.html', title='About')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = SignupForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created.', 'success')
		return redirect(url_for('home'))
	return render_template('signup.html', title='Signup', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('home'))
		else:	
			flash('Login failed. Please recheck your email and password.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/qrcode')
@login_required
def qrcode():
	return render_template('qrcode.html', title='Scan')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('launch'))

@app.route('/account')
@login_required
def account():
	return render_template('account.html', title='Account')