#!/usr/bin/env python



from application import db
from application import app

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from social.apps.flask_app.default import models
import application.models
from application.models import PostReaction

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}
@manager.command
def syncdb():
    from social.apps.flask_app.default import models
    PostReaction.metadata.create_all(db.engine)
    models.PSABase.metadata.create_all(db.engine)

if __name__ == '__main__':
    manager.run()
