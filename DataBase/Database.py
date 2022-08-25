import os

import cfg
import sqlalchemy
import sqlalchemy.ext.declarative


class dBase:
    engine = sqlalchemy.create_engine(
        'sqlite:////' + os.path.join(cfg.DB_DIR, cfg.DB_NAME), 
        connect_args={'check_same_thread':False,}, 
        echo= False
        )
    conn = engine.connect()
    base = sqlalchemy.ext.declarative.declarative_base()


class Thumbs(dBase.base):
    __tablename__ = 'thumbs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    img150 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    img200 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    img250 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    img300 = sqlalchemy.Column(sqlalchemy.LargeBinary)
    
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


class Utils(dBase):
    def Create(self):
        '''
        Removes all tables and create tables: Config, Thumbs.
        '''
        self.base.metadata.drop_all(self.conn)
        self.base.metadata.create_all(self.conn)
        
    def FillConfig(self):
        '''
        Fill Config table with necessary values.
        '''
        configValues = [
            {'name':'currColl', 'value': 'noCollection'},
            {'name':'clmns', 'value': '7'},
            {'name':'size', 'value': '150'},
            {'name':'smallScan', 'value': 'true'},
            {'name':'menuClmn', 'value': '1'},
            {'name':'typeScan', 'value': 'full'},
        ]
        
        insert = sqlalchemy.insert(Config).values(configValues)
        dBase.conn.execute(insert)





