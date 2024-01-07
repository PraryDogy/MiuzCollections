import os

import sqlalchemy

from cfg import cnf
from database import *

im = "/Volumes/Untitled/_Collections/new23/1 IMG/horse.png"


class ResetDirStats:
    def __init__(self, src: str):
        coll = src.split(os.sep)
        parrent = cnf.coll_folder.split(os.sep)
        collpath = os.path.join(*coll[:len(parrent) + 1])

        upd_dirs = (
            sqlalchemy.update(DirsMd)
            .filter(DirsMd.dirname.like(f"%{collpath}"))
            .values({"stats": "0"})
            )

        upd_main = (
            sqlalchemy.update(CollMd)
            .filter(CollMd.name.like(f"%{cnf.coll_folder}"))
            .values({"stats": "0"})
            )

        Dbase.conn.execute(upd_main)
        Dbase.conn.execute(upd_dirs)
