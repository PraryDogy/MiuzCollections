import os

import sqlalchemy

from cfg import cnf
from database import Dbase, DirsMd, ThumbsMd


class ScanDirs:
    def __init__(self):
        self.new_dirs_dict = {} # insert jpegs
        self.deldirs_dict = {} # del all jpegs with this dir, rare
        self.db_dirs = self.get_db_dirs()
        self.finder_dirs = self.get_finder_dirs()
        self.start_scandirs()

    def get_db_dirs(self):
        q = sqlalchemy.select(DirsMd.dirname, DirsMd.stats)
        res = Dbase.conn.execute(q).all()
        return {k: [int(i) for i in v.split(", ")] for k, v in res}
    
    def get_finder_dirs(self):
        finder_dirs = [os.path.join(cnf.coll_folder, i)
                   for i in os.listdir(cnf.coll_folder)
                   if os.path.isdir(os.path.join(cnf.coll_folder, i))]
    
        return {i: list(os.stat(i)) for i in finder_dirs}

    def start_scandirs(self):
        """
        Compare finder subdirs in collections folder with previous compare
        result.
        Check update_dirs_dict and deldirs_dict.
        """

        for k, v in self.db_dirs.items():
            if k not in self.finder_dirs:
                self.deldirs_dict[k] = v

        for k, v in self.finder_dirs.items():
            if k  not in self.db_dirs:
                self.new_dirs_dict[k] = v
            if k in self.db_dirs and v != self.db_dirs[k]:
                self.new_dirs_dict[k] = v


class ScanImages(ScanDirs):
    def __init__(self):
        ScanDirs.__init__(self)

        self.new_photos_list = []
        self.del_photos_list = []

        self.db_images = self.get_db_images()
        self.finder_images = [x
                              for i in self.new_dirs_dict
                              for x in self.get_finder_images(i)]

        self.start_scan_images()

    def get_db_images(self):
        """
        Load images data from database, based on "new_dirs_dict" from ScanDirs.
        Run Scandirs.start_scandirs() first.
        """
        filters = [ThumbsMd.src.like(f"%{i}%") for i in self.new_dirs_dict]
        filters = sqlalchemy.or_(*filters)

        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified).filter(filters)

        return Dbase.conn.execute(q).fetchall()

    def get_finder_images(self, dir: str):
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        images = []

        for root, dirs, files in os.walk(top=dir):
            for file in files:
                if file.endswith(exts):
                    src = os.path.join(root, file)
                    data = (src,
                            int(os.path.getsize(filename=src)),
                            int(os.stat(path=src).st_birthtime),
                            int(os.stat(path=src).st_mtime))
                    images.append(data)
        return images
    
    def start_scan_images(self):
        """
        Compare finder images data with database images data.
        Check new_photos_list and delphotos_list.
        """
        for data in self.db_images:
            if data not in self.finder_images:
                self.del_photos_list.append(data)

        for data in self.finder_images:
            if data not in self.db_images:
                self.new_photos_list.append(data)



class UpdateDb(ScanImages):
    def __init__(self):
        ScanImages.__init__(self)

    def update_dirs_db(self):
        """
        Update database with new compare result. Run "start_scandirs" first.
        """

        # объедини два словаря на удаление директорий
        # удали их одним запросом
        # и добавляй новые директории после этого


        bindparam_values = [
            {"b_dirname": k,
             "b_stats": ", ".join(str(i) for i in v)}
             for k, v in self.new_dirs_dict.items()
             ]
        
        q_del = sqlalchemy.delete(DirsMd).filter(
            DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))

        q_ins = sqlalchemy.insert(DirsMd).values(
                    {"dirname": sqlalchemy.bindparam("b_dirname"),
                     "stats": sqlalchemy.bindparam("b_stats")}
                     )

        if bindparam_values:
            Dbase.conn.execute(q_del, bindparam_values)
            Dbase.conn.execute(q_ins, bindparam_values)

        bindparam_values = [
            {"b_dirname": k}
            for k, v in self.deldirs_dict.items()
            ]
        
        q = sqlalchemy.delete(DirsMd).filter(
            DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
             
        if bindparam_values:
            Dbase.conn.execute(q, bindparam_values)