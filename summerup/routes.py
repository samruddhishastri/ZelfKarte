import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from summerup import app, db, bcrypt, mail
from summerup.models import User, Post, Todo, Item, All_items
from summerup.forms import SignupForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, CollaborateForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

def send_collaboration_email(name, email, contact_number, address, x):
	msg = Message('Collaboration Request', sender='zelfkarte@gmail.com', recipients=[x])

	msg.body = f'''A collaboration request is recieved from {name}.
Email: {email}
Contact number: {contact_number}
Address: {address}
'''

	mail.send(msg)

def send_collaboration_email_to_user(email):
	msg = Message('Collaboration Request', sender='zelfkarte@gmail.com', recipients=[email])

	msg.body = f'''Thank you for registering in Zelf Karte. Your request for collaboration has been recieved. We will contact you within next 48 hrs. through email. Please stay updated. 
'''

	mail.send(msg)
	

@app.route("/", methods=['GET', 'POST'])
def launch():
	form = CollaborateForm()

	if form.validate_on_submit():
		name = form.name.data
		email = form.email.data
		contact_number = form.contact_number.data
		address = form.address.data
		send_collaboration_email(name, email, contact_number, address, 'zelfkarte@gmail.com')
		send_collaboration_email_to_user(email)
		flash('Thank you for registering in Zelf Karte. Your request for collaboration has been recieved. We will contact you within next 48 hrs. through email. Please stay updated.', 'info')
	return render_template('launching_page.html', form=form)

@app.route("/home")
@login_required
def home():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		flash('You have been logged in as ' + current_user.username + '. Please logout from this account to sign in with different account.', 'warning')
		return redirect('home')
	form = SignupForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created.', 'success')
		login_user(user)
		return redirect(url_for('home'))
	return render_template('signup.html', title='Signup', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		flash('You have been logged in as ' + current_user.username + '.', 'warning')
		return redirect('home')
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


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your Account is Updated', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename="profile_pics/" + current_user.image_file)
	return render_template('account.html', title='Account', image_file = image_file, form = form)

@app.route("/complains")
def complains():
	page = request.args.get('page',1,type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
	return render_template('complains.html', posts=posts)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('complains'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('complains'))

@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page',1,type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='zelfkarte@gmail.com', recipients=[user.email])

	msg.body = f'''To reset your password, visit the following link: 
{url_for('reset_token', token = token, _external=True)} within 30 minutes else the token will be expired.

If you did not request for password reset, simply ignore this mail. No changes will be made to your account.
'''

	mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	user = User.verify_reset_token(token)
	if user is None:
		flash('This token is either invalid or expired.', 'warning')
		return redirect(url_for('reset_request'))
	
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Your password is updated.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/list')
@login_required
def list():
    return render_template('list.html')

@app.route('/add', methods=['POST'])
def add():
    todo = Todo(text=request.form['todoitem'], complete=False)
    db.session.add(todo)
    db.session.commit()
    current_user.todolist.append(todo)
    db.session.commit()

    return redirect(url_for('list'))

@app.route('/complete/<id>')
def complete(id):

    todo = Todo.query.filter_by(id=int(id)).first()
    todo.complete = True
    db.session.commit()
    
    return redirect(url_for('list'))

@app.route('/task_delete/<id>')
def task_delete(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    db.session.delete(todo)
    db.session.commit()
    todo.todolist = []
    db.session.commit()
    return redirect(url_for('list'))

@app.route('/delete_item/<id>')
def delete_item(id):
    item = Item.query.filter_by(id=int(id)).first()
    db.session.delete(item)
    db.session.commit()
    item.purchase = []
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/add_item', methods=['POST'])
def add_item():
    item = Item(item_name=request.form['item_name'], item_cost=request.form['item_cost'], item_quantity=request.form['item_quantity'], item_total=request.form['item_total'])
    db.session.add(item)
    db.session.commit()
    current_user.purchase.append(item)
    db.session.commit()

    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
	return render_template('qrcode.html')

@app.route('/payment')
@login_required
def payment():
	return render_template('payment.html')

@app.route('/task_Click/<id>')
def task_Click(id):
    todo = Todo.query.filter_by(id=int(id)).first()
    name_search = todo.text
    disp_item = All_items.query.filter(All_items.name.contains(name_search)).order_by(All_items.name).all()
    return render_template('search.html', disp_item=disp_item)    

@app.route("/search")
def search():
    name_search = request.args.get('name')
    disp_item = All_items.query.filter(All_items.name.contains(name_search)).order_by(All_items.name).all()
    return render_template('search.html', disp_item=disp_item)

@app.route('/delete_profile_picture', methods=['POST'])
@login_required
def delete_profile_picture():
	current_user.image_file = 'default.jpeg'
	db.session.commit()
	return redirect(url_for('account'))
