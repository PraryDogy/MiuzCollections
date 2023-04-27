import os

import sqlalchemy
import sqlalchemy.ext.declarative

import cfg


__all__ = (
    "Dbase",
    "Thumbs"
    )


class Dbase():
    """
    Checks database exists with DbChecker.

    *var conn: database connection
    *var base: declatative_base for models and actions
    """
    __engine = sqlalchemy.create_engine(
        'sqlite:////' + os.path.join(cfg.CFG_DIR, cfg.DB),
        connect_args = {'check_same_thread': False},
        echo = False
        )
    conn = __engine.connect()
    base = sqlalchemy.ext.declarative.declarative_base()


class Thumbs(Dbase.base):
    """
    Sqlalchemy model.

    *columns: img150, src, size, created, modified, collection
    """

    __tablename__ = 'thumbs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img150 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    src = sqlalchemy.Column(sqlalchemy.Text)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    created = sqlalchemy.Column(sqlalchemy.Integer)
    modified = sqlalchemy.Column(sqlalchemy.Integer)
    collection = sqlalchemy.Column(sqlalchemy.Text)
