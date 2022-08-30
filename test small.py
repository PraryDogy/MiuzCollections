import datetime
import os
import sys

import sqlalchemy

import cfg
from admin import printAlive
from DataBase.Database import Thumbs, dBase
from Utils.Utils import CreateThumb

src = '/Volumes/Shares/Marketing/Photo/2022/_Collections/00 Коллекции по камням/2022-08-24 10-28-51 копия.jpg'
fileProps = os.stat(src)
            

nSize = int(os.path.getsize(src))
nCreated = int(fileProps.st_birthtime)
nMod = int(fileProps.st_mtime)
    
# self.remove((src, size, created, mod, coll))
# q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
# dBase.conn.execute(q)

print(src, nSize, nCreated, nMod)                

