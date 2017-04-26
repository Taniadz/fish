#!/usr/bin/env python
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import config
from application import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import application.views
import application.models

