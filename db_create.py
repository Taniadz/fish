#!/usr/bin/env python
import os.path

from migrate.versioning import api

from extentions import bcrypt, db, login_manager
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from application import create_app
from social.apps.flask_app.default import models
from application.models import User
app = create_app()
app.app_context().push()
User.metadata.create_all(db.engine)
models.PSABase.metadata.create_all(db.engine)

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:

    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))