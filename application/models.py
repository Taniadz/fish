from application import db
from datetime import datetime
from flask_login import UserMixin
from application import lm
from hashlib import md5
from sqlalchemy.dialects.sqlite import BLOB

@lm.user_loader
def get_user(ident):
    return User.query.get(int(ident))


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.Integer, index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    registered_on = db.Column('registered_on', db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.LargeBinary, nullable = True)
    about_me = db.Column(db.String(140), nullable=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='com_author', lazy='dynamic')
    product_likes = db.relationship('ProductLike', backref='likes_author', lazy='dynamic')
    post_likes = db.relationship('PostLike', backref='post_likes_author', lazy='dynamic')
    products = db.relationship('Product', backref='product_author', lazy='dynamic')
    com_products = db.relationship('CommentProduct', backref='com_prod_author', lazy='dynamic')

    def __init__(self, username, password, email, avatar, about_me=None):
        self.username = username
        self.password = password
        self.email = email
        self.about_me = about_me
        self.registered_on = datetime.utcnow()
        self.avatar = avatar

        def is_authenticated(self):
            return True

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def get_id(self):
            return self.id


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(200))
    published_at = db.Column('published_at', db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    vote_count = db.Column(db.Integer, default=0)

    likes = db.relationship('PostLike', backref='current_post', lazy='dynamic')

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.published_at = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % (self.title)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    vote_count = db.Column(db.Integer, default=0)
    likes = db.relationship('CommentLike', backref='current_comment', lazy='dynamic')

    def __init__(self, text, post_id, user_id, vote_count=0, parent=0):
        self.text = text
        self.post_id = post_id
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
        self.parent = parent
        self.vote_count = vote_count

    def __repr__(self):
        return '<Comment %r>' % (self.text)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(140), nullable=True)
    published_at = db.Column(db.DateTime)
    comments = db.relationship('CommentProduct', backref='product', lazy='dynamic')
    image = db.Column(db.LargeBinary, nullable=True)
    vote_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('ProductLike', backref='current_product', lazy='dynamic')

    def __init__(self, title, description, user_id, vote_count=0):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.published_at = datetime.utcnow()
        self.vote_count = vote_count


    def __repr__(self):
        return '<Product %r>' % (self.title)


class ProductLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
    user = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    db.PrimaryKeyConstraint('product_id', 'user_id')

    def __init__(self, product, user):
        self.product = product
        self.user = user

    def __repr__(self):
        return '<ProductLike %r>' % (self.id)


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
    user = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    db.PrimaryKeyConstraint('post_id', 'user_id')

    def __init__(self, post, user):
        self.post = post
        self.user = user

    def __repr__(self):
        return '<PostLike %r>' % (self.id)


class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
    user = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    db.PrimaryKeyConstraint('comment_id', 'user_id')

    def __init__(self, comment, user):
        self.comment = comment
        self.user = user

    def __repr__(self):
        return '<CommentLike %r>' % (self.id)


class CommentProduct(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    def __init__(self, text, product_id, user_id, parent=0):
        self.text = text
        self.product_id = product_id
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
        self.parent = parent


    def __repr__(self):
        return '<CommentProduct %r>' % (self.text)