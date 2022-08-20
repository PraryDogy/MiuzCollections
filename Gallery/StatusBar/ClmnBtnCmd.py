import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Manage import Geometry, ReloadGallery


def Cmd(moreless):
    query = sqlalchemy.select(Config.value).where(Config.name=='clmns')
    res = dBase.conn.execute(query).first()[0]
    col = int(res)

    if moreless=='+':
        if col <= 10:
            col += 1
    else:
        if col > 1:
            col -=1

    query = sqlalchemy.update(Config).where(
        Config.name=='clmns').values(value=str(col))
    dBase.conn.execute(query)
    
    ReloadGallery()
    Geometry()
