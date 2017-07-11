from application import db
from datetime import datetime
from flask_login import UserMixin
from application import login_manager



@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


added_product = db.Table('added_product',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.UniqueConstraint('user_id', 'product_id', name='UC_user_id_product_id'),
)

added_post = db.Table('added_post',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.UniqueConstraint('user_id', 'post_id', name='UC_user_id_post_id'),
)

like_prod_com = db.Table('like_prod_com',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('com_product_id', db.Integer, db.ForeignKey('commentproduct.id')),
    db.UniqueConstraint('user_id', 'com_product_id', name='UC_user_id_com_product_id'),
)
like_com = db.Table('like_com',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.UniqueConstraint('user_id', 'comment_id', name='UC_user_id_com_id'),
)

like_post = db.Table('like_post',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.UniqueConstraint('user_id', 'post_id', name='UC_like_user_id_post_id'),
)

like_product = db.Table('like_product',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.UniqueConstraint('user_id', 'product_id', name='UC_like_user_id_product_id'),
)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.Integer, index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    registered_on = db.Column('registered_on', db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.LargeBinary, nullable = True)
    about_me = db.Column(db.String(1000), nullable=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='com_author', lazy='dynamic')
    products = db.relationship('Product', backref='product_author', lazy='dynamic')
    com_products = db.relationship('CommentProduct', backref='com_author', lazy='dynamic')

    added_product = db.relationship('Product', secondary=added_product, passive_deletes=True,
                           backref=db.backref('user_save', lazy='dynamic'))

    added_post = db.relationship('Post', secondary=added_post, passive_deletes=True,
                           backref=db.backref('user_save', lazy='dynamic'))
    like_post = db.relationship('Post', secondary=like_post, passive_deletes=True,
                                 backref=db.backref('user_like', lazy='dynamic'))
    like_product = db.relationship('Product', secondary=like_product, passive_deletes=True,
                                backref=db.backref('user_like', lazy='dynamic'))

    like_prod_com = db.relationship('CommentProduct', secondary=like_prod_com, passive_deletes=True,
                                   backref=db.backref('user_like', lazy='dynamic'))

    like_com = db.relationship('Comment', secondary=like_com, passive_deletes=True,
                                    backref=db.backref('user_like', lazy='dynamic'))

    def __init__(self, username, password, email, avatar=None, about_me=None):
        self.username = username
        self.password = password
        self.email = email
        self.about_me = about_me
        self.registered_on = datetime.now()
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
    title = db.Column(db.String(200))
    body = db.Column(db.String(1000))
    published_at = db.Column('published_at', db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    image = db.Column(db.LargeBinary, nullable=True)
    deleted= db.Column(db.Boolean, default=False)

    vote_count = db.Column(db.Integer, default=0)


    def __init__(self, title, body, image, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.published_at = datetime.now()
        self.image=image

    def __repr__(self):
        return '<Post %r>' % (self.title)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(800))
    image = db.Column(db.LargeBinary, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    vote_count = db.Column(db.Integer, default=0)
    deleted= db.Column(db.Boolean, default=False)

    def __init__(self, text, post_id, user_id, image, vote_count=0, parent=0):
        self.text = text
        self.post_id = post_id
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.parent = parent
        self.vote_count = vote_count
        self.image=image

    def __repr__(self):
        return '<Comment %r>' % (self.text)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(1500), nullable=True)
    price = db.Column(db.String(200), nullable=True)
    published_at = db.Column(db.DateTime)
    products = db.relationship('CommentProduct', backref='product', lazy='dynamic')
    image = db.Column(db.LargeBinary, nullable=True)
    vote_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deleted= db.Column(db.Boolean, default=False)


    def __init__(self, title, description, user_id, image,price, vote_count=0):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.published_at = datetime.now()
        self.vote_count = vote_count
        self.image=image
        self.price = price


    def __repr__(self):
        return '<Product %r>' % (self.title)







class CommentProduct(db.Model):
    __tablename__ = "commentproduct"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(800))
    image = db.Column(db.LargeBinary, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    deleted= db.Column(db.Boolean,  default=False)
    vote_count = db.Column(db.Integer, default=0)

    def __init__(self, text, product_id, user_id, image, parent=0, vote_count=0):
        self.text = text
        self.product_id = product_id
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.parent = parent
        self.vote_count = vote_count
        self.image=image


    def __repr__(self):
        return '<CommentProduct %r>' % (self.text)



