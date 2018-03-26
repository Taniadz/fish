#!/usr/bin/env python
from celery import Celery
from flask import Flask, url_for, request
from flask_mail import Mail
import flask_security
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from social_flask.routes import social_auth
import babel
from social_flask_sqlalchemy.models import init_social
#from .extentions import db
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_admin import Admin

from config import SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER, TEMPLATE_DIR, STATIC_DIR
import config
from social.apps.flask_app.template_filters import backends

from flask import g
from flask_caching import Cache


app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.from_object(config)
app.config['UPLOADS_DEFAULT_DEST'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


images = UploadSet('images', IMAGES)
configure_uploads(app, (images,))
db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app, config={'CACHE_TYPE': 'memcached', 'CACHE_MEMCACHED_SERVERS':['127.0.0.1:11211']})
cache.init_app(app)
init_social(app, db.session)





from .forms import SearchForm
# def register_extensions(app):
#     with app.app_context():
#         db.init_app(app)
#         init_social(app, db.session)
#     app.app_context().push()
def register_blueprints(app):
    """Register own and 3rd party blueprints."""
    app.register_blueprint(social_auth)

def register_before_requests(app):
    """Register before_request functions."""
    def global_user():
        g.user = current_user

    def global_from():
        g.search_form = SearchForm()
    app.before_request(global_user)
    app.before_request(global_from)

def register_context_processors(app):
    """Register context_processor functions."""
    def inject_user():
        try:
            return {'user': g.user}
        except AttributeError:
            return {'user': None}
    app.context_processor(inject_user)
    app.context_processor(backends)


def register_teardown_appcontext(app):
    """Register teardown_appcontext functions."""
    def commit_on_success(error=None):
        if error is None:
            db.session.commit()
    app.teardown_appcontext(commit_on_success)



# def create_app():
#     app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
#     app.config.from_object(config)
#     register_extensions(app)
register_blueprints(app)
register_before_requests(app)
register_context_processors(app)
register_teardown_appcontext(app)

    # return app
# app = create_app()



# init flask-security
from .forms import ExtendedConfirmRegisterForm, ExtendedRegisterForm, SearchForm
from .models import User, Role, Post, Product, Connection, PostAdmin, ProductAdmin, UserAdmin, RoleAdmin



user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedConfirmRegisterForm)
# security = Security(app, user_datastore,
#                     register_form=ExtendedRegisterForm)



# @app.before_first_request
# def before_first_request():
#
#     # Create any database tables that don't exist yet.
#     db.create_all()
#
#     # Create the Roles "admin" and "end-user" -- unless they already exist
#     user_datastore.find_or_create_role(name='admin', description='Administrator')
#
#     # Create two Users for testing purposes -- unless they already exists.
#     # In each case, use Flask-Security utility function to encrypt the password.
#     encrypted_password = flask_security.utils.encrypt_password('password')
#
#     if not user_datastore.get_user('tetianarabota@gmail.com'):
#         user_datastore.create_user(username ="Admin", email='tetianarabota@gmail.com', password=encrypted_password)
#
#     # Commit any database changes; the User and Roles must exist before we can add a Role to the User
#     db.session.commit()
#
#     # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
#     # Users already have these Roles.) Again, commit any database changes.
#     user_datastore.add_role_to_user('etianarabota@gmail.com', 'admin')
#     db.session.commit()
admin = Admin(app, name='microblog', template_mode='bootstrap3')

admin.add_view(PostAdmin(Post, db.session))
admin.add_view(ProductAdmin(Product, db.session))
# Add Flask-Admin views for Users and Roles

admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))



def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)





def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime
import application.views
import application.models







