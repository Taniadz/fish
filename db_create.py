#!/usr/bin/env python

from application import db, app



from social.apps.flask_app.default import models
from application.models import User


User.metadata.create_all(db.engine)
models.PSABase.metadata.create_all(db.engine)

