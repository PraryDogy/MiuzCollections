import os

import yadisk

import cfg
from DataBase.Database import AdminUtils

dbOutput = True


def uploadDb():
    y = yadisk.YaDisk(token=cfg.YADISK_TOKEN)
    dbPath = os.path.join(cfg.DB_DIR, cfg.DB_NAME)

    with open(dbPath, "rb") as f:
        y.upload(f, os.path.join(cfg.YADISK_DIR, cfg.DB_NAME))


def printAlive(nameFunc='', whatPrint=''):
    # print(nameFunc, whatPrint)
    return


def ClearDb():
    AdminUtils().Create()
    AdminUtils().FillConfig()
    
    