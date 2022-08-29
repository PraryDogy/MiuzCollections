import datetime
import os
import sys

import cfg
import sqlalchemy
from admin import printAlive
from DataBase.Database import Thumbs, dBase



class BaseScan(list):
    """Methods: Years, YearsAged""" 
    
    def __init__(self, aged=True):

        __baseDirs = list()
        photoDir = os.path.join(os.sep, *cfg.PHOTO_DIR.split('/')) 

        for i in range(2018, datetime.datetime.now().year + 1):
            yearDir = os.path.join(photoDir, str(i))
            __baseDirs.append(yearDir) if os.path.exists(yearDir) else None

        for year in __baseDirs:
            for dirs in os.listdir(year):
                subDir = os.path.join(year, dirs)
                self.append(subDir)

        if aged:
            days = int(cfg.FILE_AGE)
            fileAge = (
                datetime.datetime.now() - datetime.timedelta(days=days))
            youngerThan = fileAge.timestamp()

            for dir in self:
                print(dir)
                if os.stat(dir).st_birthtime > youngerThan:
                    self.remove(dir)


class ScanColls(list):
    """Inheritance: BaseScan. 
    Methods: ScanColls
    Returns list of dirs."""
    
    def __init__(self):

        collsDirs = list()
        for yearDir in BaseScan():

            if f'/{cfg.COLL_FOLDER}' in yearDir:
                collsDirs.append(yearDir)
                
        for subColl in collsDirs:
            for i in os.listdir(subColl):
                self.append(os.path.join(subColl, i))

print(BaseScan())
