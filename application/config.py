import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
FACEBOOK_APP_ID = '188477911223606'
FACEBOOK_APP_SECRET = '621413ddea2bcc5b2e83d42fc40495d'