import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils import Main as Utils


def UpdateColl():
    
    cfg.FLAG = True
    
    q = sqlalchemy.select(Config.value).where(Config.name=='currColl')
    res = dBase.conn.execute(q).first()[0]

    if 'noCollection' in res:
        Utils.CollsUpd().CollsUpd()
        Utils.RtUpd().RtAgedUpd()
        
        
    else:
        Utils.CollsUpd().CollsCurrUpd()
        

def Skip(topLevel):
    topLevel.destroy()
    cfg.FLAG = False
