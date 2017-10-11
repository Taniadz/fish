#!/usr/bin/env python
from migrate.versioning import api
from application.config import SQLALCHEMY_DATABASE_URI
from application.config import SQLALCHEMY_MIGRATE_REPO
from application import db
import os.path
db.create_all()
print SQLALCHEMY_DATABASE_URI
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))