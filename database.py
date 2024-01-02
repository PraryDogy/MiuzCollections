import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

from cfg import cnf

__all__ = (
    "Dbase",
    "ThumbsMd",
    "DirsMd",
    )


class Dbase():
    __engine = sqlalchemy.create_engine(
        "sqlite:////" + cnf.db_dir,
        connect_args = {"check_same_thread": False},
        echo = False
        )
    conn = __engine.connect()
    base = declarative_base()


class ThumbsMd(Dbase.base):
    __tablename__ = "thumbs"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img150 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    src = sqlalchemy.Column(sqlalchemy.Text)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    created = sqlalchemy.Column(sqlalchemy.Integer)
    modified = sqlalchemy.Column(sqlalchemy.Integer)
    collection = sqlalchemy.Column(sqlalchemy.Text)


class DirsMd(Dbase.base):
    __tablename__ = "dirs"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    dirname = sqlalchemy.Column(sqlalchemy.Text)
    stats = sqlalchemy.Column(sqlalchemy.Text)


Dbase.base.metadata.create_all(Dbase.conn)