#!/usr/bin/env python

import babel
from celery import Celery
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from social_flask.routes import social_auth
from social_flask_sqlalchemy.models import init_social

import config
from config import SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER, TEMPLATE_DIR, STATIC_DIR

from social.apps.flask_app.template_filters import backends

from flask import g



ALLOWED_EXTENSIONS = set(['png', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.register_blueprint(social_auth)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)




app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime



mail = Mail(app)
#
#
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

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


import application.views
import application.models



init_social(app, db.session)


def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}


app.context_processor(inject_user)
app.context_processor(backends)



