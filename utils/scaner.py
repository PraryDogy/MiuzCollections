import io
import os
import threading
from typing import Callable, Literal

import sqlalchemy
from PIL import Image, ImageOps

from cfg import cnf
from database import Dbase, DirsMd, ThumbsMd
from utils import SysUtils


__all__ = ("Scaner", )


class ScanerGlobs:
    scaner_thread = threading.Thread(target=None)
    scaner_task = None
    update = False


class CreateThumb(io.BytesIO):
    def __init__(self, src: str):
        self.ww = 150
        io.BytesIO.__init__(self)

        try:
            img = Image.open(src)
        except Exception:
            img = Image.open(cnf.thumb_err)

        img = ImageOps.exif_transpose(image=img)
        img = self.fit_thumb(img=img, w=self.ww, h=self.ww)
        img = img.convert('RGB')
        img.save(self, format="JPEG")



    def fit_thumb(self, img: Image, w: int, h: int) -> Image:
        imw, imh = img.size
        delta = imw/imh

        if delta > 1:
            neww, newh = int(h*delta), h
        else:
            neww, newh = w, int(w/delta)
        return img.resize((neww, newh))


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

        self.db_images = {}
        self.finder_images = {}

        if any((self.new_dirs, self.upd_dirs, self.del_dirs)):
            self.get_db_images()
            self.get_finder_images()
            self.compare_images()
            ScanerGlobs.update = True

    def get_db_images(self) -> dict[Literal["img path: list of ints"]]:
        dirs = [i for i in (*self.new_dirs, *self.upd_dirs, *self.del_dirs)]
        filters = [ThumbsMd.src.like(f"%{i}%") for i in dirs]
        filters = sqlalchemy.or_(*filters)

        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified).filter(filters)

        res = Dbase.conn.execute(q).fetchall()
        self.db_images.update({i[0]: i[1:None] for i in res})

    def get_finder_images(self) -> dict[Literal["img path: list of ints"]]:
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        dirs = [i for i in (*self.new_dirs, *self.upd_dirs)]

        for walk_dir in dirs:
            for root, dirs, files in os.walk(top=walk_dir):
                for file in files:

                    if not cnf.scan_status:
                        raise Exception

                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        self.finder_images[src] = (
                            int(os.path.getsize(filename=src)),
                            int(os.stat(path=src).st_birthtime),
                            int(os.stat(path=src).st_mtime))

    def compare_images(self):
        for db_src, db_stats in self.db_images.items():
            finder_stats = self.finder_images.get(db_src)
            if not finder_stats:
                self.del_images[db_src] = db_stats

        for finder_src, finder_stats in self.finder_images.items():
            db_stats = self.db_images.get(finder_src)
            if not db_stats:
                self.new_images[finder_src] = finder_stats
            if db_stats and finder_stats != db_stats:
                self.upd_images[finder_src] = finder_stats


class UpdateDb(ScanImages, SysUtils):
    def __init__(self):
        ScanImages.__init__(self)
        self.limit = 300

        if self.new_images:
            self.new_images_db()
        
        if self.upd_images:
            self.update_images_db()

        if self.del_images:
            self.delete_images_db()

        if self.new_dirs:
            self.new_dirs_db()
        
        if self.upd_dirs:
            self.update_dirs_db()

        if self.del_dirs:
            self.delete_dirs_db()

    def new_dirs_db(self):
        insert_values = [
            {"b_dirname": dirname, "b_stats": ",".join(str(i) for i in stats)}
             for dirname, stats in self.new_dirs.items()]

        insert_dirs = (
            sqlalchemy.insert(DirsMd)
            .values({"dirname": sqlalchemy.bindparam("b_dirname"),
                     "stats": sqlalchemy.bindparam("b_stats")})
                     )

        Dbase.conn.execute(insert_dirs, insert_values)

    def update_dirs_db(self):
        update_values = [
            {"b_dirname": dirname, "b_stats": ",".join(str(i) for i in stats)}
            for dirname, stats in self.upd_dirs.items()]
        
        update_dirs = (
            sqlalchemy.update(DirsMd)
            .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
            .values({"stats": sqlalchemy.bindparam("b_stats")})
            )
             
        Dbase.conn.execute(update_dirs, update_values)

    def delete_dirs_db(self):
        delete_values = [
            {"b_dirname": dirname}
            for dirname, stats in self.del_dirs.items()]
        
        delete_dirs = (
            sqlalchemy.delete(DirsMd)
            .filter(DirsMd.dirname == sqlalchemy.bindparam("b_dirname"))
            )
        
        Dbase.conn.execute(delete_dirs, delete_values)

    def new_images_db(self):
        values = []
        
        for src, (size, created, modified) in self.new_images.items():

            if not cnf.scan_status:
                raise Exception

            values.append(
                {"b_img150": CreateThumb(src=src).getvalue(),
                 "b_src": src,
                 "b_size": size,
                 "b_created": created,
                 "b_modified": modified,
                 "b_collection": self.get_coll_name(src=src)})

 
        values = [values[i : i + self.limit]
                    for i in range(0, len(values), self.limit)]

        for chunk in values:

            if not cnf.scan_status:
                raise Exception

            insert_images = (
                sqlalchemy.insert(ThumbsMd)
                .values({"img150": sqlalchemy.bindparam("b_img150"),
                         "src": sqlalchemy.bindparam("b_src"),
                         "size": sqlalchemy.bindparam("b_size"),
                         "created": sqlalchemy.bindparam("b_created"),
                         "modified": sqlalchemy.bindparam("b_modified"),
                         "collection": sqlalchemy.bindparam("b_collection")})
                         )
            Dbase.conn.execute(insert_images, chunk)

    def update_images_db(self):
        values = []

        for src, (size, created, modified) in self.upd_images.items():

            if not cnf.scan_status:
                raise Exception
            
            values.append(
                {"b_img150": CreateThumb(src=src).getvalue(),
                 "b_src": src,
                 "b_size": size,
                 "b_created": created,
                 "b_modified": modified})

        values = [values[i : i + self.limit]
                    for i in range(0, len(values), self.limit)]

        for chunk in values:

            if not cnf.scan_status:
                raise Exception

            update_images = (
                sqlalchemy.update(ThumbsMd)
                .values({"img150": sqlalchemy.bindparam("b_img150"),
                         "size": sqlalchemy.bindparam("b_size"),
                         "created": sqlalchemy.bindparam("b_created"),
                         "modified": sqlalchemy.bindparam("b_modified")})
                .filter(ThumbsMd.src == sqlalchemy.bindparam("b_src"))
                )
            Dbase.conn.execute(update_images, chunk)

    def delete_images_db(self):
        values = [
            {"b_src": src}
            for src, stats in self.del_images.items()]

        values = [values[i : i + self.limit]
                    for i in range(0, len(values), self.limit)]

        for chunk in values:

            if not cnf.scan_status:
                raise Exception

            delete_images = (
                sqlalchemy.delete(ThumbsMd)
                .filter(ThumbsMd.src == sqlalchemy.bindparam("b_src"))
                )
            Dbase.conn.execute(delete_images, chunk)


class ScanerThread(SysUtils):
    def __init__(self):
        cnf.scan_status = False
        while ScanerGlobs.scaner_thread.is_alive():
            cnf.root.update()

        cnf.stbar_btn().configure(text=cnf.lng.updating, fg_color=cnf.blue_color)
        cnf.scan_status = True
        ScanerGlobs.scaner_thread = threading.Thread(target=UpdateDb, daemon=True)
        ScanerGlobs.scaner_thread.start()

        while ScanerGlobs.scaner_thread.is_alive():
            cnf.root.update()

        if cnf.curr_coll != cnf.all_colls:
            coll = os.path.join(cnf.coll_folder, cnf.curr_coll)
            if not os.path.exists(coll):
                cnf.curr_coll = cnf.all_colls

        if ScanerGlobs.update:
            cnf.reload_thumbs()
            cnf.reload_menu()
            try:
                Dbase.conn.execute("VACUUM")
            except Exception:
                print(self.print_err())
            ScanerGlobs.update = False

        cnf.stbar_btn().configure(text=cnf.lng.update, fg_color=cnf.btn_color)
        cnf.scan_status = False


class Scaner(SysUtils):
    def __init__(self):
        if ScanerGlobs.scaner_task:
            cnf.root.after_cancel(ScanerGlobs.scaner_task)

        if self.smb_check():
            print("run scaner")
            ScanerThread()

        ScanerGlobs.scaner_task = cnf.root.after(
            ms=cnf.scan_time * 1000, func=__class__)