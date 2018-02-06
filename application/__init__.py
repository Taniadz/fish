#!/usr/bin/env python
# from flask_login import current_user
import babel
from celery import Celery
from flask import Flask
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from social_flask.routes import social_auth
from social_flask_sqlalchemy.models import init_social
from .extentions import db
#
#
from config import SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER, TEMPLATE_DIR, STATIC_DIR
import config
from social.apps.flask_app.template_filters import backends

from flask import g




ALLOWED_EXTENSIONS = set(['png', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.from_object(config)
db = SQLAlchemy(app)

init_social(app, db.session)

def register_extensions(app):
    """Register Flask extensions."""
    # bcrypt.init_app(app)

    with app.app_context():
        db.init_app(app)
        init_social(app, db.session)
    app.app_context().push()


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



# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI








def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime



mail = Mail(app)

from .forms import ExtendedRegisterForm
from .models import User, Role, Connection

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
         register_form=ExtendedRegisterForm)



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




# register_extensions(app)
register_blueprints(app)
register_before_requests(app)
register_context_processors(app)
register_teardown_appcontext(app)


import application.views
import application.models






