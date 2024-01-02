import os

import sqlalchemy

from cfg import cnf
from database import Dbase, DirsMd, ThumbsMd
from  typing import Literal

class ScanDirs:
    def __init__(self):
        self.new_dirs = {} # insert DirsMd query
        self.upd_dirs = {} # same above, but update
        self.del_dirs = {} # same above, but delete

        self.db_dirs = self.get_db_dirs()
        self.finder_dirs = self.get_finder_dirs()

        self.compare_dirs()

    def get_db_dirs(self) -> dict[Literal["path: list of ints"]]:
        q = sqlalchemy.select(DirsMd.dirname, DirsMd.stats)
        res = Dbase.conn.execute(q).all()
        return {k: [int(i) for i in v.split(",")] for k, v in res}
    
    def get_finder_dirs(self) -> dict[Literal["path: list of ints"]]:
        finder_dirs = [os.path.join(cnf.coll_folder, i)
                   for i in os.listdir(cnf.coll_folder)
                   if os.path.isdir(os.path.join(cnf.coll_folder, i))]
    
        return {i: list(os.stat(i)) for i in finder_dirs}

    def compare_dirs(self):
        """
        Compare finder subdirs in collections folder with previous compare
        result.
        Check new_dirs, upd_dirs and upd_dirs.
        """
        for db_src, db_stats in self.db_dirs.items():
            if db_src not in self.finder_dirs:
                self.del_dirs[db_src] = db_stats

        for finder_src, finder_stats in self.finder_dirs.items():
            db_stats = self.db_dirs.get(finder_src)
            if not db_stats:
                self.new_dirs[finder_src] = finder_stats
            if db_stats and finder_stats != db_stats:
                self.upd_dirs[finder_src] = finder_stats


class ScanImages(ScanDirs):
    def __init__(self):
        ScanDirs.__init__(self)

        self.new_images = {} # insert ThumbsMd query
        self.upd_images = {} # same above, but update
        self.del_images = {} # same above, but delete

        self.db_images = self.get_db_images()
        self.finder_images: dict = self.get_finder_images()

        self.compare_images()

    def get_db_images(self) -> dict[Literal["img path: list of ints"]]:
        """
        Load images data from database, based on "new_dirs_dict" from ScanDirs.
        Run Scandirs.start_scandirs() first.
        """
        filters = [ThumbsMd.src.like(f"%{i}%") for i in self.new_dirs]
        filters = sqlalchemy.or_(*filters)

        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified).filter(filters)

        res = Dbase.conn.execute(q).fetchall()
        return {i[0]: i[1:None] for i in res}

    def get_finder_images(self) -> dict[Literal["img path: list of ints"]]:
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        images = {}
        walk_dirs = [i for i in (*self.new_dirs, *self.upd_dirs)]

        for walk_dir in walk_dirs:
            for root, dirs, files in os.walk(top=walk_dir):
                for file in files:
                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        images[src] = (
                            int(os.path.getsize(filename=src)),
                            int(os.stat(path=src).st_birthtime),
                            int(os.stat(path=src).st_mtime))
        return images
    
    def compare_images(self):
        """
        Compare finder images data with database images data.
        Check new_photos_list and delphotos_list.
        """
        for db_src, db_stats in self.db_images.items():
            if db_src not in self.finder_images:
                self.del_images[db_src] = db_stats

        for finder_src, finder_stats in self.finder_images.items():
            db_stats = self.db_images.get(finder_src)
            if not db_stats:
                self.new_images[finder_src] = finder_stats
            if db_stats and finder_stats != db_stats:
                self.upd_images[finder_src] = finder_stats


class Queries(ScanImages):
    def __init__(self):
        ScanImages.__init__(self)

    def update_dirs_db(self):
        """
        Update database with new compare result. Run "start_scandirs" first.
        """

        insert_values = [
            {"b_dirname": dirname, "b_stats": ",".join(str(i) for i in stats)}
             for dirname, stats in self.new_dirs.items()]

        insert_dirs = (
            sqlalchemy.insert(DirsMd)
            .values({"dirname": sqlalchemy.bindparam("b_dirname"),
                     "stats": sqlalchemy.bindparam("b_stats")})
                     )

        if insert_values:
            Dbase.conn.execute(insert_dirs, insert_values)

        update_values = [
            {"b_dirname": dirname, "b_stats": ",".join(str(i) for i in stats)}
            for dirname, stats in self.upd_dirs.items()]
        
        update_dirs = (
            sqlalchemy.update(DirsMd)
            .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
            .values({"stats": sqlalchemy.bindparam("b_stats")})
            )
             
        if update_values:
            print(update_dirs)
            Dbase.conn.execute(update_dirs, update_values)

        delete_values = [
            {"b_dirname": dirname}
            for dirname, stats in self.del_dirs.items()]
        
        delete_dirs = (
            sqlalchemy.delete(DirsMd)
            .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
            )
        
        if delete_values:
            Dbase.conn.execute(delete_dirs, delete_values)