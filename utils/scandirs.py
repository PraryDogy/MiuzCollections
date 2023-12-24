import os

import sqlalchemy

from cfg import cnf
from database import Dbase, DirsMd, ThumbsMd


class ScanDirs:
    def __init__(self):
        self.newdirs_dict = {}
        self.updatedirs_dict = {}
        self.deldirs_dict = {}

        scaned_dirs = [os.path.join(cnf.coll_folder, i)
                   for i in os.listdir(cnf.coll_folder)
                   if os.path.isdir(os.path.join(cnf.coll_folder, i))]
    
        scaned_dirs = {i: list(os.stat(i))
                   for i in scaned_dirs}
        
        q = sqlalchemy.select(DirsMd.dirname, DirsMd.stats)
        dbdirs = Dbase.conn.execute(q).all()

        dbdirs = {k: [int(i) for i in v.split(", ")]
                  for k, v in dbdirs}

        for k, v in scaned_dirs.items():
            if k  not in dbdirs:
                self.newdirs_dict[k] = v
            if k in dbdirs and v != dbdirs[k]:
                self.updatedirs_dict[k] = v

        for k, v in dbdirs.items():
            if k not in scaned_dirs:
                self.deldirs_dict[k] = v

    def update_db(self):
        newdirs = [
            {f"b_dirname": k,
             f"b_stats": ", ".join(str(i) for i in v)}
             for k, v in self.newdirs_dict.items()
            ]
        
        q = sqlalchemy.insert(DirsMd).values(
                    {"dirname": sqlalchemy.bindparam("b_dirname"),
                     "stats": sqlalchemy.bindparam("b_stats")}
                     )
        if newdirs:
            Dbase.conn.execute(q, newdirs)

        updatedirs = [
            {f"b_dirname": k,
             f"b_stats": ", ".join(str(i) for i in v)}
             for k, v in self.updatedirs_dict.items()
            ]
        
        q = (sqlalchemy.update(DirsMd)
             .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
             .values({"stats": sqlalchemy.bindparam("b_stats")})
             )
        
        if updatedirs:
            Dbase.conn.execute(q, updatedirs)

        deldirs = [
            {"b_dirname": k}
             for k, v in self.deldirs_dict.items()
            ]
        
        q = sqlalchemy.delete(DirsMd).filter(
            DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
             
        if deldirs:
            Dbase.conn.execute(q, deldirs)


class DelColls:
    def __init__(self):
        q = sqlalchemy.select(DirsMd.dirname)
        colls = [i[0] for i in Dbase.conn.execute(q).all()]
    
        filters = [ThumbsMd.src.not_like(f"%{i}%") for i in colls]
        filters = sqlalchemy.or_(*filters)        
        q = sqlalchemy.delete(ThumbsMd).filter(*filters)
