import os
import threading

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd

from .image import ImageUtils
from .system import SysUtils

__all__ = ("scaner",)


class Scaner(ImageUtils, SysUtils):
    def __init__(self) -> None:
        self.__need_update = False
        self.__scaner_task = None

    def scaner_sheldue(self, default_time: int = cnf.scan_time*60000):
        if self.__scaner_task:
            cnf.root.after_cancel(id=self.__scaner_task)
        ms = default_time
        self.__scaner_task = cnf.root.after(ms=ms, func=self.scaner_start_now)

    def scaner_start_now(self):

        cnf.scan_status = True
        cnf.stbar_btn().configure(text=cnf.lng.updating, fg_color=cnf.blue_color)

        cnf.scaner_thread = threading.Thread(target=self.task, daemon=True)
        cnf.scaner_thread.start()

        while cnf.scaner_thread.is_alive():
            cnf.root.update()

        self.__change_live_text("")

        if self.__need_update:
            cnf.reload_thumbs()
            cnf.reload_menu()

            try:
                Dbase.conn.execute("VACUUM")
            except Exception:
                print(self.print_err())

            self.__need_update = False

        cnf.scan_status = False
        cnf.stbar_btn().configure(text=cnf.lng.update, fg_color=cnf.btn_color)

        self.scaner_sheldue()

    def task(self):
        self.__change_live_text(cnf.lng.preparing)

        db_images = Dbase.conn.execute(sqlalchemy.select(
            ThumbsMd.src, ThumbsMd.size, ThumbsMd.created, ThumbsMd.modified)
            ).fetchall()

        collections = [os.path.join(cnf.coll_folder, i)
                       for i in os.listdir(path=cnf.coll_folder)
                       if not i.startswith((".", "_"))]

        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")
        ln = len(collections)
        new_images = []
        found_images = []

        for x, collection in enumerate(iterable=collections, start=1):
            self.__change_live_text(
                    f"{cnf.lng.scaning} {x} {cnf.lng.from_pretext} "
                    f"{ln} {cnf.lng.colls_case}."
                    )

            if not os.path.isdir(s=collection):
                if collection.endswith(exts):
                    data = (collection,
                            int(os.path.getsize(filename=collection)),
                            int(os.stat(path=collection).st_birthtime),
                            int(os.stat(path=collection).st_mtime))
                    found_images.append(data)

                    if data not in db_images:
                        new_images.append(data)

            for root, dirs, files in os.walk(top=collection):

                if not cnf.scan_status:
                    return

                for file in files:

                    if not cnf.scan_status:
                        return

                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        data = (src,
                                int(os.path.getsize(filename=src)),
                                int(os.stat(path=src).st_birthtime),
                                int(os.stat(path=src).st_mtime))
                        found_images.append(data)

                        if data not in db_images:
                            new_images.append(data)

        if new_images:
            self.__need_update = True
            ln = len(new_images)

            values = [
                {"b_img150": self.encode_image(src=src),
                 "b_src": src,
                 "b_size": size,
                 "b_created": created,
                 "b_modified": modified,
                 "b_collection": self.get_coll_name(src=src),
                 "temp": self.__change_live_text(
                        f"{cnf.lng.added} {x} {cnf.lng.from_pretext} "
                        f"{ln} {cnf.lng.new_photo_case}.")
                        }
                for x, (src, size, created, modified) in enumerate(iterable=new_images, start=1)
                if cnf.scan_status
                ]

            limit = 300
            values = [values[i : i + limit]
                      for i in range(0, len(values), limit)]

            for vals in values:
                
                if not cnf.scan_status:
                    return

                q = sqlalchemy.insert(ThumbsMd).values(
                    {"img150": sqlalchemy.bindparam("b_img150"),
                     "src": sqlalchemy.bindparam("b_src"),
                     "size": sqlalchemy.bindparam("b_size"),
                     "created": sqlalchemy.bindparam("b_created"),
                     "modified": sqlalchemy.bindparam("b_modified"),
                     "collection": sqlalchemy.bindparam("b_collection")}
                     )
                Dbase.conn.execute(q, vals)

        remove_images = []

        for src, size, created, modified in db_images:
            if not cnf.scan_status:
                return

            if (src, size, created, modified) not in found_images:
                remove_images.append((src, size, created, modified))

        if remove_images:

            self.__need_update = True

            values = [
                {"b_src": src,
                 "b_size": size,
                 "b_created": created,
                 "b_modified": modified
                 }
                 for src, size, created, modified in remove_images
                 if cnf.scan_status
                 ]

            limit = 300
            values = [values[i : i + limit]
                      for i in range(0, len(values), limit)]

            ln_vals = len(values)
            for x, vals in enumerate(iterable=values, start=1):
                self.__change_live_text(
                    f"{cnf.lng.finishing} {x} {cnf.lng.from_pretext} {ln_vals}"
                    )

                if not cnf.scan_status:
                    return

                q = sqlalchemy.delete(ThumbsMd).filter(
                    ThumbsMd.src == sqlalchemy.bindparam("b_src"),
                    ThumbsMd.size == sqlalchemy.bindparam("b_size"),
                    ThumbsMd.created == sqlalchemy.bindparam("b_created"),
                    ThumbsMd.modified == sqlalchemy.bindparam("b_modified")
                    )
                Dbase.conn.execute(q, vals)

    def __change_live_text(self, text):
        cnf.scan_win_txt = text


scaner = Scaner()