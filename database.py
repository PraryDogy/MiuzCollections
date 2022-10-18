"""
Database module.
"""

import os

import sqlalchemy
import sqlalchemy.ext.declarative

import cfg


class Dbase():
    """
    Checks database exists with DbChecker.

    *var conn: database connection
    *var base: declatative_base for models and actions
    """
    __engine = sqlalchemy.create_engine(
        'sqlite:////' + os.path.join(cfg.DB_DIR, 'database.db'),
        connect_args={'check_same_thread':False,},
        echo= False
        )
    conn = __engine.connect()
    base = sqlalchemy.ext.declarative.declarative_base()


class Thumbs(Dbase.base):
    """
    Sqlalchemy model.

    *columns: img150, src, size, created, modified,
    collection
    """

    __tablename__ = 'thumbs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img150 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    src = sqlalchemy.Column(sqlalchemy.Text)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    created = sqlalchemy.Column(sqlalchemy.Integer)
    modified = sqlalchemy.Column(sqlalchemy.Integer)
    collection = sqlalchemy.Column(sqlalchemy.Text)


class Config(Dbase.base):
    """
    Sqlalchemy model.

    :param: name, value
    """

    __tablename__ = 'config'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Text)
    value = sqlalchemy.Column(sqlalchemy.Text)


class Utils:
    """
    Methods for database.

    *method create: removes all tables, creates new,
    *method fill_config: fills "Config" table with default values
    """
    def create(self):
        """
        Removes all tables and create tables: Config, Thumbs
        """

        Dbase.base.metadata.drop_all(Dbase.conn)
        Dbase.base.metadata.create_all(Dbase.conn)

    def fill_config(self):
        """Fill Config table with necessary values."""

        cfg_values = [
            {'name':'currColl', 'value': 'last'},
            {'name':'size', 'value': '150'},
            {'name':'typeScan', 'value': 'full'},
        ]

        insert = sqlalchemy.insert(Config).values(cfg_values)
        Dbase.conn.execute(insert)
