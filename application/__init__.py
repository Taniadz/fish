#!/usr/bin/env python
import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore

from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from . import config
from .config import SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_DATABASE_URI

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static/media')
ALLOWED_EXTENSIONS = set(['png', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'tetianarabota@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Gfhjksot11041988'
# app.config['MAIL_DEFAULT_SENDER'] = 'Default sender name'
mail = Mail(app)
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_REGISTER_URL'] = '/create_account'
app.config['SECURITY_PASSWORD_SALT'] = 'ddddsdv123'

app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': '1631777696846006',
    'consumer_secret': '988af003ce0c2f1b35140a80cd146cdb'
}
app.config['SECURITY_POST_LOGIN'] = '/login'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

from .forms import ExtendedRegisterForm
from .models import User, Role, Connection

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
         register_form=ExtendedRegisterForm)


app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

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
#
# @celery.task()
# def add_together(a, b):
#     return a + b

import application.views
import application.models