from utils.scandirs import ScanDirs, DelColls
import sqlalchemy
from database import Dbase, DirsMd, ThumbsMd


scandirs = ScanDirs()
scandirs.update_db()

# print(scandirs.deldirs_dict)
# print(scandirs.newdirs_dict)
# print(scandirs.updatedirs_dict)

class DelColls:
    def __init__(self):
        q = sqlalchemy.select(DirsMd.dirname)
        colls = [i[0] for i in Dbase.conn.execute(q).all()]
    
        filters = [ThumbsMd.src.not_like(f"%{i}%") for i in colls]
        filters = sqlalchemy.or_(*filters)        
        q = sqlalchemy.delete(ThumbsMd).filter(*filters)

