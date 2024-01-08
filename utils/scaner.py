import io
import os
import threading
from typing import Literal

import sqlalchemy
from PIL import Image, ImageOps

from cfg import cnf
from database import Dbase, ThumbsMd

from .system import CreateThumb, SysUtils

__all__ = ("FullScaner", "ScanerGlobs", )


class ScanerGlobs:
    thread = threading.Thread(target=None)
    update = False
    task = False


class SetProgressbar:
    def onestep(self):
        cnf.progressbar_var.set(value=cnf.progressbar_var.get() + 0.25)

    def set(self, value):
        cnf.progressbar_var.set(value=value)


class ScanImages:
    def __init__(self):
        self.new_images = {} # insert ThumbsMd query
        self.upd_images = {} # same above, but update
        self.del_images = {} # same above, but delete

        self.db_images = {}
        self.finder_images = {}

        self.get_db_images()
        self.get_finder_images()
        self.compare_images()

        ScanerGlobs.update = True
        SetProgressbar().onestep()

    def get_db_images(self) -> dict[Literal["img path: list of ints"]]:
        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified)

        res = Dbase.conn.execute(q).fetchall()
        self.db_images.update({i[0]: i[1:] for i in res})

    def get_finder_images(self) -> dict[Literal["img path: list of ints"]]:
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        for root, dirs, files in os.walk(top=cnf.coll_folder):
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


        SetProgressbar().onestep()


class DublicateRemover:
    def __init__(self):
        q = sqlalchemy.select(ThumbsMd.id, ThumbsMd.src)
        res = Dbase.conn.execute(q).fetchall()
        res = {i[0]: i[1] for i in res}

        dublicates = {}
        for k, v in res.items():
            if not dublicates.get(v):
                dublicates[v] = [k]
            else:
                dublicates[v].append(k)

        dublicates = [row_id
                      for _, id_list in dublicates.items()
                      for row_id in id_list[1:]
                      if len(v) > 1]
        
        if not dublicates:
            return

        values = [{"b_id": i} for i in dublicates]
        q = (sqlalchemy.delete(ThumbsMd)
             .filter(ThumbsMd.id==sqlalchemy.bindparam("b_id")))
        Dbase.conn.execute(q, values)


class UpdateDb(ScanImages, SysUtils):
    def __init__(self):
        ScanImages.__init__(self)
        TrashRemover()
        DublicateRemover()
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


class FullScanThread(SysUtils):
    def __init__(self):
        cnf.scan_status = False
        while ScanerGlobs.thread.is_alive():
            cnf.root.update()

        cnf.stbar_btn().configure(text=cnf.lng.updating, fg_color=cnf.blue_color)
        cnf.scan_status = True
        ScanerGlobs.thread = threading.Thread(target=UpdateDb, daemon=True)
        ScanerGlobs.thread.start()

        while ScanerGlobs.thread.is_alive():
            cnf.root.update()

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


class FullScaner(SysUtils):
    def __init__(self):
        SetProgressbar().set(value=0)

        if self.smb_check():
            FullScanThread()

        else:
            if ScanerGlobs.task:
                cnf.root.after_cancel(ScanerGlobs.task)
            ScanerGlobs.task = cnf.root.after(ms=10000, func=__class__)

        SetProgressbar().set(value=1)
