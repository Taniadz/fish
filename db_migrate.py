#!/usr/bin/env python


from social_flask_sqlalchemy.models import init_social

from application import db
from application import app

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

init_social(app, db.session)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()
