import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils import Main as Utils


def UpdateColl():
    cfg.FLAG = True
    Utils.CollsUpd().CollsUpd()
    Utils.RtUpd().RtAgedUpd()


def Skip(topLevel):
    topLevel.destroy()
    cfg.FLAG = False
