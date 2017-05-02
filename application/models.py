from application import db
from datetime import datetime
from flask_login import UserMixin
from application import lm
#
@lm.user_loader
def get_user(ident):
  return User.query.get(int(ident))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.Integer, index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140), nullable=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='com_author', lazy='dynamic')
    registered_on = db.Column('registered_on', db.DateTime)

    def __init__(self, username, password, email, about_me):
        self.username = username
        self.password = password
        self.email = email
        self.about_me = about_me
        self.registered_on = datetime.utcnow()

        def is_authenticated(self):
            return True

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def get_id(self):
            return self.id


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(200))
    published_at = db.Column('published_at', db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.published_at = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % (self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    def __init__(self, text, post_id, user_id, parent=0):
        self.text = text
        self.post_id = post_id
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
        self.parent = parent

    def __repr__(self):
        return '<Comment %r>' % (self.text)
