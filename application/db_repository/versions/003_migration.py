from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
comment = Table('comment', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('timestamp', DateTime),
    Column('content', String),
    Column('user_id', Integer),
    Column('post_id', Integer),
    Column('com_to_com', Integer),
)

comment = Table('comment', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('timestamp', DateTime),
    Column('text', String(length=140)),
    Column('user_id', Integer),
    Column('post_id', Integer),
    Column('com_to_com', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comment'].columns['content'].drop()
    post_meta.tables['comment'].columns['text'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['comment'].columns['content'].create()
    post_meta.tables['comment'].columns['text'].drop()
