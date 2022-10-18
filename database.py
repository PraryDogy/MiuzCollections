"""
Database module.
"""

import os
import shutil
import threading
import tkinter

import sqlalchemy
import sqlalchemy.ext.declarative

import cfg
from utils.utils import MyLabel


class DbChecker(tkinter.Toplevel):
    """
    Checks database folder and database file. Creates folder if not exists.
    Downloads prepared database from yandex disk if file not exists.
    Creates empty database and create tables with the
    required values if download fails.
    """

    def __init__(self):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=10)
        self.withdraw()
        self.__check()

    def __check(self):
        """
        Checks database folder and database file.
        Creates folder if not exists.
        Downloads prepared database from yandex disk if file not exists.
        Creates empty database and create tables with the
        required values if download fails.
        """

        if not os.path.exists(cfg.DB_DIR):
            os.makedirs(cfg.DB_DIR)

        db_path = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
        if not os.path.exists(db_path) or os.path.getsize(db_path) < 0.9:

            self.__gui()
            check_db = threading.Thread(target=self.__download_db)
            check_db.start()

            while check_db.is_alive():
                cfg.ROOT.update()

        self.destroy()

    def __download_db(self):
        """
        Downloads prepared database file from yandex disk or
        create new one with tables and values if download fails.
        """

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), 'database.db'),
            os.path.join(cfg.DB_DIR, cfg.DB_NAME),
            )

    def __gui(self):
        """
        Creates gui while database is downloading.
        """

        self.focus_force()
        self.title('Подождите')
        self.resizable(0,0)

        descr = MyLabel(self, text='Скачиваю дополнения.')
        descr.pack(pady=10, padx=10)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()


class Dbase(DbChecker):
    """
    Checks database exists with DbChecker.

    *var conn: database connection
    *var base: declatative_base for models and actions
    """
    DbChecker()
    __engine = sqlalchemy.create_engine(
        'sqlite:////' + os.path.join(cfg.DB_DIR, cfg.DB_NAME),
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
