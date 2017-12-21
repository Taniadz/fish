from application import db
from datetime import datetime
from application import login_manager


from flask_security import UserMixin, RoleMixin

@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


favourite_product = db.Table('favourite_product',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.UniqueConstraint('user_id', 'product_id', name='UC_user_id_product_id'),
)

favourite_post = db.Table('favourite_post',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.UniqueConstraint('user_id', 'post_id', name='UC_user_id_post_id'),
)


class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    filename = db.Column(db.String)
    image = db.relationship('Product', passive_deletes=True,  backref='image')



class PostReaction(db.Model):
    __tablename__ = 'postreaction'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    type = db.Column(db.Integer)
    posts = db.relationship('Post', passive_deletes=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='post_user'),
                      )


class ProductReaction(db.Model):
    __tablename__ = 'productreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    type = db.Column(db.Integer)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='product_user'),
                      )



class PostComReaction(db.Model):
    __tablename__ = 'postcomreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    type = db.Column(db.Integer)
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='comment_user'),
                      )



class ProdComReaction(db.Model):
    __tablename__ = 'prodcomreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), )
    comment_id = db.Column(db.Integer, db.ForeignKey('commentproduct.id'))
    type = db.Column(db.Integer)
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='prod_comment_user'),
                      )


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    registered_on = db.Column('registered_on', db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.String, nullable=True)
    avatar_min = db.Column(db.String, nullable=True)
    about_me = db.Column(db.String(1000), nullable=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='com_author', lazy='dynamic')
    products = db.relationship('Product', backref='product_author', lazy='dynamic')
    com_products = db.relationship('CommentProduct', backref='com_author', lazy='dynamic')

    favourite_product = db.relationship('Product', secondary=favourite_product, passive_deletes=True,
                           backref='favourite')

    favourite_post = db.relationship('Post', secondary=favourite_post, passive_deletes=True,
                           backref='favourite')

    post_react = db.relationship('PostReaction', passive_deletes=True,
                                 backref='user_like')
    product_react = db.relationship('ProductReaction', backref='user_like')

    prod_com_react = db.relationship('ProdComReaction', passive_deletes=True,
                                   backref='user_like')

    post_com_react = db.relationship('PostComReaction', passive_deletes=True,
                                    backref='user_like')

    def __init__(self, username, password, email, roles, active):
        self.username = username
        self.password = password
        self.email = email
        self.roles = roles
        self.active = active
        self.registered_on = datetime.now()



    def get_security_payload(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)



class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1000))
    published_at = db.Column('published_at', db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    image = db.Column(db.String, nullable=True)
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('PostReaction',
                            backref=db.backref('post',  passive_deletes=True))

    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)

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
    image = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('PostComReaction',
                                backref=db.backref('post', passive_deletes=True))


    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('ProductReaction',
                                backref=db.backref('post', passive_deletes=True))

    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)

    def __init__(self, title, description, user_id,price, vote_count=0):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.published_at = datetime.now()
        self.vote_count = vote_count
        self.price = price


    def __repr__(self):
        return '<Product %r>' % (self.title)




class CommentProduct(db.Model):
    __tablename__ = "commentproduct"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(800))
    image = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    parent = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    deleted= db.Column(db.Boolean,  default=False)

    reactions = db.relationship('ProdComReaction',
                                backref=db.backref('post', passive_deletes=True))
    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)

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



