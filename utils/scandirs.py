import os

import sqlalchemy

from cfg import cnf
from database import Dbase, DirsMd


class ScanDirs:
    def __init__(self):
        self.newdirs = {}
        self.updatedirs = {}
        self.deldirs = {}

    def start(self):
        scaned_dirs = [os.path.join(cnf.coll_folder, i)
                   for i in os.listdir(cnf.coll_folder)
                   if os.path.isdir(os.path.join(cnf.coll_folder, i))]
    
        scaned_dirs = {i: list(os.stat(i))
                   for i in scaned_dirs}
        
        q = sqlalchemy.select(DirsMd.dirname, DirsMd.stats)
        dbdirs = Dbase.conn.execute(q).all()

        dbdirs = {k: [int(i) for i in v.split(", ")]
                  for k, v in dbdirs}
        
        self.compare(dbdirs=dbdirs, scaned_dirs=scaned_dirs)
        

    def compare(self, dbdirs: dict, scaned_dirs: dict):
        for k, v in scaned_dirs.items():
            if k  not in dbdirs:
                self.newdirs[k] = v
            if k in dbdirs and v != dbdirs[k]:
                self.updatedirs[k] = v

        for k, v in dbdirs.items():
            if k not in scaned_dirs:
                self.deldirs[k] = v

    def add_to_db(self):
        newdirs = [
            {f"b_dirname": k,
             f"b_stats": ", ".join(str(i) for i in v)}
             for k, v in self.newdirs.items()
            ]
        
        q = sqlalchemy.insert(DirsMd).values(
                    {"dirname": sqlalchemy.bindparam("b_dirname"),
                     "stats": sqlalchemy.bindparam("b_stats")}
                     )
        Dbase.conn.execute(q, newdirs)

        # print("need new dir")

    def update_db(self):
        updatedirs = [
            {f"b_dirname": k,
             f"b_stats": ", ".join(str(i) for i in v)}
             for k, v in self.updatedirs.items()
            ]
        
        q = (sqlalchemy.update(DirsMd)
             .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
             .values({"stats": sqlalchemy.bindparam("b_stats")})
             )
        
        Dbase.conn.execute(q, updatedirs)

        # print("need update dir")


    def delete_db(self):
        deldirs = [
            {"b_dirname": k}
             for k, v in self.deldirs.items()
            ]
        
        q = sqlalchemy.delete(DirsMd).filter(
            DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
             
        Dbase.conn.execute(q, deldirs)

        # print("need delete")

    def delete_dirsmd(self):
        if self.deldirs:
            self.delete_db()

    def update_dirsmd(self):        
        if self.updatedirs:
            self.update_db()

        if self.newdirs:
            self.add_to_db()

