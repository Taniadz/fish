from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
connection = Table('connection', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('provider_id', String(length=255)),
    Column('provider_user_id', String(length=255)),
    Column('access_token', String(length=255)),
    Column('secret', String(length=255)),
    Column('display_name', String(length=255)),
    Column('profile_url', String(length=512)),
    Column('image_url', String(length=512)),
    Column('rank', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('email', String(length=255)),
    Column('password', String(length=255)),
    Column('active', Boolean),
    Column('confirmed_at', DateTime),
    Column('registered_on', DateTime),
    Column('last_seen', DateTime),
    Column('avatar', LargeBinary),
    Column('avatar_min', LargeBinary),
    Column('about_me', String(length=1000)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['connection'].create()
    post_meta.tables['user'].columns['avatar_min'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['connection'].drop()
    post_meta.tables['user'].columns['avatar_min'].drop()
