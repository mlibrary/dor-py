import sqlalchemy

from dor.config import config


def get_db_session():
    engine = sqlalchemy.create_engine(config.get_database_engine_url())
    with sqlalchemy.orm.Session(engine) as session:
        yield session
