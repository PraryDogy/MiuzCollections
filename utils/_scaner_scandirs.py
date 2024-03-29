import io
import os
import threading
from typing import Literal

import sqlalchemy
from PIL import Image, ImageOps

from cfg import cnf
from database import Dbase, DirsMd, ThumbsMd, CollMd
from utils import SysUtils

__all__ = ("Scaner", "ResetDirStats", )


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


class Storage:
    _thread = threading.Thread(target=None)
    _task = None
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

        newimg = img.copy()
        img.close()

        newimg = newimg.convert('RGB')
        newimg.save(self, format="JPEG")


    def fit_thumb(self, img: Image, w: int, h: int) -> Image:
        imw, imh = img.size
        delta = imw/imh

        if delta > 1:
            neww, newh = int(h*delta), h
        else:
            neww, newh = w, int(w/delta)
        return img.resize((neww, newh))


class SetProgressbar:
    def onestep(self):
        cnf.progressbar_var.set(value=cnf.progressbar_var.get() + 0.12)

    def set(self, value):
        cnf.progressbar_var.set(value=value)


class ScanMain:
    def __init__(self):
        q = (sqlalchemy.select(CollMd.stats)
             .filter(CollMd.name==cnf.coll_folder))
        
        self.db_coll_stats = Dbase.conn.execute(q).first()
        self.finder_coll_stats = ",".join(
            str(i) for i in os.stat(cnf.coll_folder))

        if self.db_coll_stats:
            if self.db_coll_stats[0] == self.finder_coll_stats:
                raise Exception("\n\nMain check: no scan needed\n\n")

    def update_main(self):
        if not self.db_coll_stats:
            Dbase.conn.execute(sqlalchemy.delete(CollMd))
            q = (sqlalchemy.insert(CollMd)
                 .values({"name": cnf.coll_folder,
                          "stats": self.finder_coll_stats}))
            Dbase.conn.execute(q)

        else:
            q = (sqlalchemy.update(CollMd)
                 .filter(CollMd.name==cnf.coll_folder)
                 .values({"stats": self.finder_coll_stats}))
            Dbase.conn.execute(q)


class ScanDirs(ScanMain):
    def __init__(self):
        ScanMain.__init__(self)

        self.new_dirs = {} # insert DirsMd query
        self.upd_dirs = {} # same above, but update
        self.del_dirs = {} # same above, but delete

        self.db_dirs = self.get_db_dirs()
        self.finder_dirs = self.get_finder_dirs()

        self.compare_dirs()

        SetProgressbar().onestep()

        if not any((self.new_dirs, self.upd_dirs, self.del_dirs)):
            raise Exception("\n\nDirs check: no scan needed\n\n")

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

        self.get_db_images()
        self.get_finder_images()
        self.compare_images()

        Storage.update = True
        SetProgressbar().onestep()

    def get_db_images(self) -> dict[Literal["img path: list of ints"]]:
        dirs = [i for i in (*self.new_dirs, *self.upd_dirs, *self.del_dirs)]
        filters = [ThumbsMd.src.like(f"%{i}%") for i in dirs]
        filters = sqlalchemy.or_(*filters)

        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified).filter(filters)

        res = Dbase.conn.execute(q).fetchall()
        self.db_images.update({i[0]: i[1:] for i in res})

    def get_finder_images(self) -> dict[Literal["img path: list of ints"]]:
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        dirs = [i for i in (*self.new_dirs, *self.upd_dirs)]

        for walk_dir in dirs:
            for root, dirs, files in os.walk(top=walk_dir):
                for file in files:

                    if not cnf.scan_status:
                        raise Exception("\n\nScaner stopped by scan_status")

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


class TrashRemover:
    def __init__(self):
        coll = cnf.coll_folder + os.sep

        q = (sqlalchemy.select(ThumbsMd.src)
            .filter(ThumbsMd.src.not_like(f"%{coll}%")))
        trash_img = Dbase.conn.execute(q).first()

        if trash_img:
            q = (sqlalchemy.delete(ThumbsMd)
                .filter(ThumbsMd.src.not_like(f"%{coll}%")))
            Dbase.conn.execute(q)

        q = (sqlalchemy.select(DirsMd.dirname)
            .filter(DirsMd.dirname.not_like(f"%{coll}%")))
        trash_dir = Dbase.conn.execute(q).first()

        if trash_dir:
            q = (sqlalchemy.delete(DirsMd)
                .filter(DirsMd.dirname.not_like(f"%{coll}%")))
            Dbase.conn.execute(q)

        q = sqlalchemy.select(CollMd).filter(CollMd.name!=cnf.coll_folder)
        trash_main = Dbase.conn.execute(q).first()

        if trash_main:
            q = sqlalchemy.delete(CollMd).filter(CollMd.name!=cnf.coll_folder)
            Dbase.conn.execute(q)

        SetProgressbar().onestep()


class UpdateDb(ScanImages, SysUtils, TrashRemover):
    def __init__(self):
        ScanImages.__init__(self)
        TrashRemover.__init__(self)
        self.limit = 300

        if self.new_images:
            self.new_images_db()

        SetProgressbar().onestep()

        if self.upd_images:
            self.update_images_db()

        SetProgressbar().onestep()

        if self.del_images:
            self.delete_images_db()

        SetProgressbar().onestep()

        if self.new_dirs:
            self.new_dirs_db()
        
        if self.upd_dirs:
            self.update_dirs_db()

        if self.del_dirs:
            self.delete_dirs_db()

        self.update_main()

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
                raise Exception("\n\nScaner stopped by scan_status")

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
                raise Exception("\n\nScaner stopped by scan_status")

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
                raise Exception("\n\nScaner stopped by scan_status")
            
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
                raise Exception("\n\nScaner stopped by scan_status")

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
                raise Exception("\n\nScaner stopped by scan_status")

            delete_images = (
                sqlalchemy.delete(ThumbsMd)
                .filter(ThumbsMd.src == sqlalchemy.bindparam("b_src"))
                )
            Dbase.conn.execute(delete_images, chunk)


class ScanerThread(SysUtils):
    def __init__(self):
        cnf.scan_status = False
        while Storage._thread.is_alive():
            cnf.root.update()

        cnf.stbar_btn().configure(text=cnf.lng.updating, fg_color=cnf.blue_color)
        cnf.scan_status = True
        Storage._thread = threading.Thread(target=UpdateDb, daemon=True)
        Storage._thread.start()

        while Storage._thread.is_alive():
            cnf.root.update()

        if Storage.update:
            cnf.reload_thumbs()
            cnf.reload_menu()
            try:
                Dbase.conn.execute("VACUUM")
            except Exception:
                print(self.print_err())
            Storage.update = False

        cnf.stbar_btn().configure(text=cnf.lng.update, fg_color=cnf.btn_color)
        cnf.scan_status = False


class Scaner(SysUtils):
    def __init__(self):
        SetProgressbar().set(value=0)

        if Storage._task:
            cnf.root.after_cancel(Storage._task)

        if self.smb_check():
            ScanerThread()

        Storage._task = cnf.root.after(
            ms=cnf.scan_time_sec * 1000, func=__class__)

        SetProgressbar().set(value=1)
