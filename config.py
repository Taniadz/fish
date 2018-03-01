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
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "https://aqua.name/crop_image"
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_USER_MODEL = 'application.models.User'

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_KEY = '1631777696846006'
SOCIAL_AUTH_FACEBOOK_SECRET= '988af003ce0c2f1b35140a80cd146cdb'
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'id, name, email, age_range'
}
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'application.views.save_profile',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',


)
#


# flask-security settings
SECURITY_CONFIRMABLE = True
SECURITY_EMAIL_SENDER = 'contact.me@aqua.name'

SECURITY_REGISTERABLE = True
SECURITY_REGISTER_URL = '/create_account'
SECURITY_POST_REGISTER_VIEW = "/confirm"
SECURITY_PASSWORD_SALT = 'ddddsdv123'
SECURITY_POST_LOGIN = '/'
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_CHANGEABLE = True

MAIL_SERVER = 'smtp.zoho.eu'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = True
MAIL_USERNAME = 'contact.me@aqua.name'
MAIL_PASSWORD = 'password'
# MAIL_USERNAME = 'mail.aqua.fish@gmail.com'
# MAIL_PASSWORD = 'mail_aqua_fish23101994'

# celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


ALLOWED_EXTENSIONS = set(['png', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
