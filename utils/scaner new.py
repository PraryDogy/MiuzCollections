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
    def onestep(self, value=0.1):
        cnf.progressbar_var.set(value=cnf.progressbar_var.get() + value)

    def to_start(self):
        cnf.progressbar_var.set(value=0.0)

    def to_end(self):
        cnf.progressbar_var.set(value=1.0)


class OldCollFolderRemover:
    def __init__(self):
        coll_folder = cnf.coll_folder + os.sep

        q = (sqlalchemy.select(ThumbsMd.src)
            .filter(ThumbsMd.src.not_like(f"%{coll_folder}%")))
        trash_img = Dbase.conn.execute(q).first()

        if trash_img:
            q = (sqlalchemy.delete(ThumbsMd)
                .filter(ThumbsMd.src.not_like(f"%{coll_folder}%")))
            Dbase.conn.execute(q)


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


class GetImages:
    def __init__(self):
        self.db_images = {}
        self.finder_images = {}

        self.get_db_images()
        self.get_finder_images()
        # ScanerGlobs.update = True

    def get_db_images(self) -> dict[Literal["img path: list of ints"]]:
        q = sqlalchemy.select(ThumbsMd.src, ThumbsMd.size, ThumbsMd.created,
                              ThumbsMd.modified)

        res = Dbase.conn.execute(q).fetchall()
        self.db_images.update({i[0]: i[1:] for i in res})

    def get_finder_images(self) -> dict[Literal["img path: list of ints"]]:
        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        collections = []

        for i in os.listdir(cnf.coll_folder):
            collection = os.path.join(cnf.coll_folder, i)
            if not os.path.isdir(collection):
                continue
            if i.startswith("_"):
                continue
            collections.append(collection)

        steps_count = 0.8 / len(collections)

        for collection_walk in collections:
            SetProgressbar().onestep(value=steps_count)
            for root, dirs, files in os.walk(top=collection_walk):
                for file in files:

                    if not cnf.scan_status:
                        raise Exception("\n\nScaner stopped by scan_status")

                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        self.finder_images[src] = (
                            int(os.path.getsize(filename=src)),
                            int(os.stat(path=src).st_birthtime),
                            int(os.stat(path=src).st_mtime))


class CompareImages(GetImages):
    def __init__(self):
        CompareImages.__init__(self)
        self.images = {"insert": {}, "update": {}, "delete": {}}

        for db_src, db_stats in self.db_images.items():
            finder_stats = self.finder_images.get(db_src)
            if not finder_stats:
                # self.del_images[db_src] = db_stats
                self.images["delete"][db_src] = db_stats

        for finder_src, finder_stats in self.finder_images.items():
            db_stats = self.db_images.get(finder_src)
            if not db_stats:
                # self.new_images[finder_src] = finder_stats
                self.images["insert"][finder_src] = finder_stats
            if db_stats and finder_stats != db_stats:
                # self.upd_images[finder_src] = finder_stats
                self.images["update"][finder_src] = finder_stats


class UpdateDb(CompareImages, SysUtils):
    def __init__(self):
        CompareImages.__init__(self)
        self.limit = 300

        for k, v in self.images.items():
            if v:
                values = self.create_bindparam(key=k)

        # if self.new_images:
            # self.new_images_db()

        # if self.upd_images:
            # self.update_images_db()

        # SetProgressbar().onestep()

        # if self.del_images:
            # self.delete_images_db()

        # SetProgressbar().onestep()

        # OldCollFolderRemover()
        # DublicateRemover()
                
    def create_bindparam(self, key: Literal["insert", "update", "delete"]):
        values = []

        for src, (size, created, modified) in self.images[key].items():

            if not cnf.scan_status:
                    raise Exception("Scaner stopped by scan_status")

            data = {"b_src": src}

            if key != "delete":
                data.update({"b_img150": CreateThumb(src=src).getvalue(),
                             "b_size": size,
                             "b_created": created,
                             "b_modified": modified,
                             "b_collection": self.get_coll_name(src=src)})
                
            values.append(data)

        chunks = [values[i : i + self.limit]
                    for i in range(0, len(values), self.limit)]

        queries = []

        if key == "insert":
            q = sqlalchemy.insert(ThumbsMd)
        elif key == "update":
            q = sqlalchemy.update(ThumbsMd)
        else:
            q = sqlalchemy.delete(ThumbsMd)

        for chunk in chunks:
            if key in ("insert", "update"):
                query = q.values(
                    {"img150": sqlalchemy.bindparam("b_img150"),
                    "src": sqlalchemy.bindparam("b_src"),
                    "size": sqlalchemy.bindparam("b_size"),
                    "created": sqlalchemy.bindparam("b_created"),
                    "modified": sqlalchemy.bindparam("b_modified"),
                    "collection": sqlalchemy.bindparam("b_collection")}
                    )
            
            if key in ("update", "delete"):
                query = q.filter(ThumbsMd.src == sqlalchemy.bindparam("b_src"))
            

    def new_images_db(self):
        values = [] 
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

        cnf.stbar_btn().configure(fg_color=cnf.blue_color, text=cnf.lng.updating)
        cnf.scan_status = True
        SetProgressbar().to_start()
        ScanerGlobs.thread = threading.Thread(target=UpdateDb, daemon=True)
        ScanerGlobs.thread.start()

        while ScanerGlobs.thread.is_alive():
            cnf.root.update()
        SetProgressbar().to_end()

        if ScanerGlobs.update:
            cnf.reload_thumbs()
            cnf.reload_menu()
            try:
                Dbase.conn.execute("VACUUM")
            except Exception:
                print(self.print_err())
            ScanerGlobs.update = False

        cnf.stbar_btn().configure(fg_color=cnf.bg_color, text=cnf.lng.update)
        cnf.scan_status = False


class FullScaner(SysUtils):
    def __init__(self):

        if self.smb_check():
            FullScanThread()
            if ScanerGlobs.task:
                cnf.root.after_cancel(ScanerGlobs.task)
            ScanerGlobs.task = cnf.root.after(ms=3600000, func=__class__)

        else:
            if ScanerGlobs.task:
                cnf.root.after_cancel(ScanerGlobs.task)
            ScanerGlobs.task = cnf.root.after(ms=10000, func=__class__)

