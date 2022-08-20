import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


class dBase:

    parent = os.path.dirname(__file__)

    engine = sqlalchemy.create_engine(
        f'sqlite:///{parent}/database.db', 
        connect_args={'check_same_thread':False,}, 
        echo= False
        )
    conn = engine.connect()
    base = declarative_base()


class Files(dBase.base):
    __tablename__ = 'files'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img = sqlalchemy.Column(sqlalchemy.BLOB)
    src = sqlalchemy.Column(sqlalchemy.Text)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    created = sqlalchemy.Column(sqlalchemy.Integer)
    modified = sqlalchemy.Column(sqlalchemy.Integer)
    collection = sqlalchemy.Column(sqlalchemy.Text)


class Config(dBase.base):
    __tablename__ = 'config'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Text)
    value = sqlalchemy.Column(sqlalchemy.Text)
    
    
def Again():
    dBase.base.metadata.drop_all(dBase.conn)
    dBase.base.metadata.create_all(dBase.conn)
    
    q = sqlalchemy.insert(Config).values(name='currColl', value='9 Liola')
    dBase.conn.execute(q)
    
# Again()