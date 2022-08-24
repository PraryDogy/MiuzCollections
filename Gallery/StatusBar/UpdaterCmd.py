import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils import Scaner

def UpdateColl():
    cfg.FLAG = True
    Scaner.CollsUpd().CollsUpd()
    Scaner.RtUpd().RtAgedUpd()


def Skip(topLevel):
    topLevel.destroy()
    cfg.FLAG = False
