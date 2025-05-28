import sqlalchemy

from dor.config import config


def get_db_session():
    engine = sqlalchemy.create_engine(config.get_database_engine_url())
    with sqlalchemy.orm.Session(engine) as session:
        yield session


def get_inbox_path():
    return config.inbox_path


def get_pending_path():
    return config.filesets_path
