# from .extentions import db
from application import db, app
from datetime import datetime
from flask_security import UserMixin, RoleMixin
import flask_security
from wtforms import PasswordField
from flask_admin.contrib import  sqla
from time import time
import json


from flask_security import current_user
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('photo_id', db.Integer, db.ForeignKey('post.id')),
                )



class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True)
    description = db.Column(db.String(1000))
    regional = db.Column(db.Boolean, default = False)
    image = db.Column(db.String(300), nullable=True)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

class FavouriteProduct(db.Model):
    __tablename__ = 'favourite_products'
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='favourite_product_user'),
    )

class FavouritePost(db.Model):
    __tablename__ ='favourite_posts'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='favourite_post_user'),
    )



class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    filename = db.Column(db.String(3000))
    image = db.relationship('Product', passive_deletes=True,  backref='image')



class PostReaction(db.Model):
    __tablename__ = 'postreaction'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    type = db.Column(db.String(10))
    posts = db.relationship('Post')
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='post_user'),
                      )


class ProductReaction(db.Model):
    __tablename__ = 'productreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    type = db.Column(db.String(10))
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='product_user'),
                      )



class PostComReaction(db.Model):
    __tablename__ = 'postcomreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    type = db.Column(db.String(10))
    comments = db.relationship('Comment')

    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='comment_user'),
                      )



class ProdComReaction(db.Model):
    __tablename__ = 'prodcomreaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), )
    comment_id = db.Column(db.Integer, db.ForeignKey('commentproduct.id'))
    type = db.Column(db.String(10))
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
    username = db.Column(db.String(64),unique=True, index=True)
    last_name = db.Column(db.String(64))


    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    registered_on = db.Column('registered_on', db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.String(3000), nullable=True)
    avatar_min = db.Column(db.String(3000), nullable=True)
    social= db.Column(db.Boolean, default=False, nullable=False)

    about_me = db.Column(db.String(1000), nullable=True)

    posts = db.relationship('Post', backref='author')
    notifications = db.relationship('Notification')

    comments = db.relationship('Comment', backref='com_author')
    products = db.relationship('Product')

    com_products = db.relationship('CommentProduct', backref='com_author')


    post_react = db.relationship('PostReaction', passive_deletes=True,
                                 backref='user_like')
    product_react = db.relationship('ProductReaction', backref='user_like')

    prod_com_react = db.relationship('ProdComReaction', passive_deletes=True,
                                   backref='user_like')

    post_com_react = db.relationship('PostComReaction', passive_deletes=True,
                                    backref='user_like')
    allow_mail_notification = db.Column(db.Boolean, default=True)
    profile_settings = db.Column(db.JSON)
    def __init__(self, username, email, password="?", roles=[], active=True):
        self.username = username
        self.password = password
        self.email = email
        self.roles = roles
        self.active = active
        self.registered_on = datetime.now()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n




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
    title = db.Column(db.String(300))
    body = db.Column(db.String(2500))
    published_at = db.Column('published_at', db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    image = db.Column(db.String(3000), nullable=True)
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('PostReaction',
                            backref=db.backref('post'))
    favourites = db.relationship(FavouritePost,passive_deletes=True )

    tags = db.relationship('Tag', secondary=tags, backref='posts')
    topic_id = db.Column(db.Integer, nullable=True)


    like_count = db.Column(db.Integer, default=0)
    unlike_count = db.Column(db.Integer, default=0)
    funny_count = db.Column(db.Integer, default=0)
    angry_count = db.Column(db.Integer, default=0)


    def __init__(self, title, body, image, user_id, topic_id):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.published_at = datetime.now()
        self.image=image
        self.topic_id = topic_id



    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.DateTime)
    text = db.Column(db.String(800))
    image = db.Column(db.String(3000), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.Column(db.Integer, nullable=True)
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('PostComReaction',
                                backref=db.backref('post'))


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
    __searchable__ = ['description']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), unique=True)
    description = db.Column(db.String(1500), nullable=True)
    price = db.Column(db.String(200), nullable=True)
    published_at = db.Column(db.DateTime)
    products = db.relationship('CommentProduct', backref='product', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deleted= db.Column(db.Boolean, default=False)
    reactions = db.relationship('ProductReaction',
                                backref=db.backref('post'))
    favourites = db.relationship(FavouriteProduct,passive_deletes=True )



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
    image = db.Column(db.String(3000), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    parent = db.Column(db.Integer, nullable=True)
    deleted= db.Column(db.Boolean,  default=False)

    reactions = db.relationship('ProdComReaction',
                                backref=db.backref('post'))
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




from math import ceil

class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num



# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = flask_security.utils.encrypt_password(model.password2)



# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Customized Role model for SQL-Admin
class PostAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')




# Customized Role model for SQL-Admin
class TopicAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Customized Role model for SQL-Admin
class ProductAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

class Notification(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    closeable = db.Column(db.Boolean, default=True)
    closed = db.Column(db.Boolean, default=False)
    payload_json = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


    def get_data(self):
        return json.loads(str(self.payload_json))



class Dialog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_text = db.Column(db.String(150))
    readed = db.Column(db.Boolean, default=False)
    last_massage_date = db.Column(db.DateTime)
    last_receiver = db.Column(db.Integer, db.ForeignKey('user.id'))
    participants = db.Column(db.JSON)




class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(3000))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    participants = db.Column(db.JSON)
    dialog_id = db.Column(db.Integer, db.ForeignKey('dialog.id'))
    readed = db.Column(db.Boolean, default=False)
    sent_at  = db.Column(db.DateTime)
    file = db.Column(db.String(3000), nullable=True)
    def __init__(self, text, sender_id, receiver_id, file, dialog_id, participants):
        self.text = text
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.sent_at = datetime.now()
        self.file = file
        self.dialog_id = dialog_id
        self.participants=participants



