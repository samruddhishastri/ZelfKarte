from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from summerup import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

purchase = db.Table('purchase',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)

todolist = db.Table('todolist',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('list_id', db.Integer, db.ForeignKey('todo.id'))
)

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable = False, default = 'default.jpeg')
	password = db.Column(db.String(60), nullable=False)
	posts = db.relationship('Post', backref='author', lazy=True)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Boolean)
    listers = db.relationship('User', secondary=todolist, backref=db.backref('todolist', lazy='dynamic'))

class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	item_name = db.Column(db.String(20))
	item_cost = db.Column(db.Integer)
	item_quantity = db.Column(db.Integer)
	item_total = db.Column(db.Integer)
	buyers = db.relationship('User', secondary=purchase, backref=db.backref('purchase', lazy='dynamic'))