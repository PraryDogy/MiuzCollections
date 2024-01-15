import io
import os
import threading
from typing import Literal

import sqlalchemy
from PIL import Image, ImageOps

from cfg import cnf
from database import Dbase, ThumbsMd

from .system import CreateThumb, SysUtils

__all__ = ("Scaner", "Storage", )


class Storage:
    scaner_thread = threading.Thread(target=None)
    scaner_schedule = False
    need_gui_reload = False


class SetProgressbar:
    def onestep(self, value=0.1):
        cnf.progressbar_var.set(value=cnf.progressbar_var.get() + value)

    def to_start(self):
        cnf.progressbar_var.set(value=0.0)

    def to_end(self):
        cnf.progressbar_var.set(value=1.0)


class StopScaner:
    def __init__(self) -> None:
        if not cnf.scan_status:
            raise Exception("Scaner stopped by cnf.scan_status")


class StBarBtn:
    def set_updating(self):
        cnf.stbar_btn().configure(fg_color=cnf.blue_color,
                                  text=cnf.lng.updating)
        
    def set_normal(self):
        cnf.stbar_btn().configure(fg_color=cnf.bg_color,
                                  text=cnf.lng.update)


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

        steps_count = 1 / len(collections)

        for collection_walk in collections:
            SetProgressbar().onestep(value=steps_count)
            for root, dirs, files in os.walk(top=collection_walk):
                for file in files:

                    StopScaner()

                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        self.finder_images[src] = (
                            int(os.path.getsize(filename=src)),
                            int(os.stat(path=src).st_birthtime),
                            int(os.stat(path=src).st_mtime))


class CompareImages(GetImages):
    def __init__(self):
        GetImages.__init__(self)
        self.images = {"insert": {}, "update": {}, "delete": {}}

        for db_src, db_stats in self.db_images.items():
            finder_stats = self.finder_images.get(db_src)
            if not finder_stats:
                self.images["delete"][db_src] = db_stats

        for finder_src, finder_stats in self.finder_images.items():
            db_stats = self.db_images.get(finder_src)
            if not db_stats:
                self.images["insert"][finder_src] = finder_stats
            if db_stats and finder_stats != db_stats:
                self.images["update"][finder_src] = finder_stats


class SetUpdateStatus(CompareImages):
    def __init__(self):
        CompareImages.__init__(self)

        for k, v in self.images.items():
            if v:
                Storage.need_gui_reload = True
                return


class UpdateDb(SetUpdateStatus, SysUtils):
    def __init__(self):
        SetUpdateStatus.__init__(self)
        self.limit = 300

        for k, v in self.images.items():
            if v:
                self.create_bindparam(key=k)
                
    def create_bindparam(self, key: Literal["insert", "update", "delete"]):
        values = []

        for src, (size, created, modified) in self.images[key].items():
            StopScaner()
            data = {"b_src": src}
            if key != "delete":
                data.update(
                    {"b_img150": CreateThumb(src=src).getvalue(),
                     "b_size": size,
                     "b_created": created,
                     "b_modified": modified,
                     "b_collection": self.get_coll_name(src=src)})
            values.append(data)

        chunks = [values[i : i + self.limit]
                    for i in range(0, len(values), self.limit)]

        for chunk in chunks:
            StopScaner()
            if key == "insert":
                query = sqlalchemy.insert(ThumbsMd)
            elif key == "update":
                query = sqlalchemy.update(ThumbsMd)
            else:
                query = sqlalchemy.delete(ThumbsMd)
            if key in ("insert", "update"):
                query = query.values(
                    {"img150": sqlalchemy.bindparam("b_img150"),
                    "src": sqlalchemy.bindparam("b_src"),
                    "size": sqlalchemy.bindparam("b_size"),
                    "created": sqlalchemy.bindparam("b_created"),
                    "modified": sqlalchemy.bindparam("b_modified"),
                    "collection": sqlalchemy.bindparam("b_collection")})
            if key in ("update", "delete"):
                query = query.filter(
                    ThumbsMd.src == sqlalchemy.bindparam("b_src"))
                
            Dbase.conn.execute(query, chunk)


class ScanerBase(UpdateDb):
    def __init__(self):
        UpdateDb.__init__(self)
        OldCollFolderRemover()
        DublicateRemover()


class ScanerThread(SysUtils):
    def __init__(self):
        cnf.scan_status = False
        while Storage.scaner_thread.is_alive():
            cnf.root.update()

        StBarBtn().set_updating()
        cnf.scan_status = True
        SetProgressbar().to_start()
        Storage.scaner_thread = threading.Thread(target=UpdateDb, daemon=True)
        Storage.scaner_thread.start()

        while Storage.scaner_thread.is_alive():
            cnf.root.update()
        SetProgressbar().to_end()

        if Storage.need_gui_reload:
            cnf.reload_thumbs()
            cnf.reload_menu()
            try:
                Dbase.conn.execute("VACUUM")
            except Exception:
                print(self.print_err())
            Storage.need_gui_reload = False

        StBarBtn().set_normal()
        cnf.scan_status = False


class Scaner(SysUtils):
    def __init__(self):

        if self.smb_check():
            ScanerThread()
            if Storage.scaner_schedule:
                cnf.root.after_cancel(Storage.scaner_schedule)
            Storage.scaner_schedule = cnf.root.after(ms=3600000, func=__class__)

        else:
            if Storage.scaner_schedule:
                cnf.root.after_cancel(Storage.scaner_schedule)
            Storage.scaner_schedule = cnf.root.after(ms=10000, func=__class__)
