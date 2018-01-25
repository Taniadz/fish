import os
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

TEMPLATE_DIR = os.path.join(basedir, 'templates')
STATIC_DIR= os.path.join(basedir, "static")

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'


# settings for python social auth---------------------------------------------------
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = ('social.backends.google.GoogleOAuth2', \
                                                    'social.backends.facebook.FacebookOAuth2')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "http://myapp.com/"
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_USER_MODEL = 'application.models.User'

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_KEY = '1631777696846006'
SOCIAL_AUTH_FACEBOOK_SECRET= '988af003ce0c2f1b35140a80cd146cdb'
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'id, name, email, age_range'
}

# app.config["SOCIAL_AUTH_PIPELINE"] = (
#     'application.views.save_profile',
#     'social_core.pipeline.social_auth.social_details',
#     'social_core.pipeline.social_auth.social_uid',
#     'social_core.pipeline.social_auth.auth_allowed',
#     'social_core.pipeline.social_auth.social_user',
#     'social_core.pipeline.user.get_username',
#     'common.pipeline.require_email',
#     'social_core.pipeline.mail.mail_validation',
#     'social_core.pipeline.user.create_user',
#     'social_core.pipeline.social_auth.associate_user',
#     'social_core.pipeline.debug.debug',
#     'social_core.pipeline.social_auth.load_extra_data',
#     'social_core.pipeline.user.user_details',
#     'social_core.pipeline.debug.debug'
# )
#


# flask-security settings
SECURITY_CONFIRMABLE = False
SECURITY_EMAIL_SENDER = 'no-reply@example.com'

SECURITY_REGISTERABLE = True
SECURITY_REGISTER_URL = '/create_account'
SECURITY_PASSWORD_SALT = 'ddddsdv123'
SECURITY_POST_LOGIN = '/'

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'mail.aqua.fish@gmail.com'
MAIL_PASSWORD = 'mail_aqua_fish23101994'

# celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'