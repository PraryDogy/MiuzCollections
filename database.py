import os

import sqlalchemy
import sqlalchemy.ext.declarative

from cfg import cnf

__all__ = (
    "Dbase",
    "Thumbs"
    )


class Dbase():
    __engine = sqlalchemy.create_engine(
        'sqlite:////' + cnf.db_dir,
        connect_args = {'check_same_thread': False},
        echo = False
        )
    conn = __engine.connect()
    base = sqlalchemy.ext.declarative.declarative_base()


class Thumbs(Dbase.base):
    __tablename__ = 'thumbs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img150 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    src = sqlalchemy.Column(sqlalchemy.Text)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    created = sqlalchemy.Column(sqlalchemy.Integer)
    modified = sqlalchemy.Column(sqlalchemy.Integer)
    collection = sqlalchemy.Column(sqlalchemy.Text)
