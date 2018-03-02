#!/usr/bin/env python
from celery import Celery
from flask import Flask, url_for, request
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from social_flask.routes import social_auth
import babel
from social_flask_sqlalchemy.models import init_social
#from .extentions import db
from flask_uploads import UploadSet, IMAGES, configure_uploads


from config import SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER, TEMPLATE_DIR, STATIC_DIR
import config
from social.apps.flask_app.template_filters import backends

from flask import g
from flask_caching import Cache



app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.from_object(config)
app.config['UPLOADS_DEFAULT_DEST'] = UPLOAD_FOLDER

images = UploadSet('images', IMAGES)
configure_uploads(app, (images,))
db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app, config={'CACHE_TYPE': 'memcached', 'CACHE_MEMCACHED_SERVERS':['127.0.0.1:11211']})
cache.init_app(app)
init_social(app, db.session)




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
    app.before_request(global_user)

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
from .forms import ExtendedConfirmRegisterForm, ExtendedRegisterForm
from .models import User, Role, Connection

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedConfirmRegisterForm)
# security = Security(app, user_datastore,
#                     register_form=ExtendedRegisterForm)


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







