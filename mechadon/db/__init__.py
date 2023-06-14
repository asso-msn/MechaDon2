import sqlalchemy as sa
from sqlalchemy import MetaData, orm

from mechadon import config

from .base import Base as Base_

meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base: Base_ = orm.declarative_base(cls=Base_, metadata=meta)

session = None
engine = None


def setup_db(url=None, force=False):
    global engine, session
    if not force and session is not None:
        return
    url = url or config.db_url
    engine = sa.create_engine(url)
    Session = orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()


setup_db()


def update_or_create(model, filter_keys=None, **kwargs):
    filter_keys = filter_keys or []
    result = (
        session.query(model)
        .filter_by(
            **{
                key: value
                for key, value in kwargs.items()
                if key in filter_keys
            }
        )
        .first()
    )
    if result:
        for key, value in kwargs.items():
            setattr(result, key, value)
        return result
    result = model(**kwargs)
    session.add(result)
    return result


Id = sa.Integer
