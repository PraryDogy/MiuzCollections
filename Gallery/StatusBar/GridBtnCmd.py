import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Utils import *


def Cmd(moreless):
    query = sqlalchemy.select(Config.value).where(Config.name=='size')
    size = int(dBase.conn.execute(query).first()[0])

    if moreless=='+':
        if size < 300:
            size += 50
            query = sqlalchemy.update(Config).where(
                Config.name=='size').values(value=str(size))
            dBase.conn.execute(query)

    if moreless=='-':
        if size > 150:
            size -= 50
            query = sqlalchemy.update(Config).where(
                Config.name=='size').values(value=str(size))
            dBase.conn.execute(query)

    ReloadGallery()
