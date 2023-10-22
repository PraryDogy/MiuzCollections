import os

import sqlalchemy

from cfg import cnf
from database import Dbase, Thumbs

from .globals import Globals
from .utils import *
import threading


__all__ = (
    "scaner",
    )


class Scaner:
    def __init__(self) -> None:
        self.need_update = False
        self.scaner_task = None

    def scaner_sheldue(self):
        cnf.root.after_cancel(self.task)
        ms = cnf.scan_time*60000
        self.scaner_task = cnf.root.after(ms, self.scaner_start)

    def scaner_start(self):
        print("scan")
        cnf.scan_flag = True
        Globals.stbar_btn.configure(text=cnf.lang.updating,bg=cnf.topbar_color)

        cnf.scaner_task = threading.Thread(target=self.task, daemon=True)
        cnf.scaner_task.start()

        while cnf.scaner_task.is_alive():
            cnf.root.update()

        self.__change_live_text("")

        if self.need_update:
            Globals.reload_thumbs()
            Globals.reload_menu()
            self.need_update = False

        cnf.scan_flag = False
        Globals.stbar_btn.configure(text=cnf.lang.update, bg=cnf.btn_color)

        self.scaner_sheldue()

    def task(self):
        self.__change_live_text(cnf.lang.preparing)

        db_images = Dbase.conn.execute(
            sqlalchemy.select(
            Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified
            )
            ).fetchall()

        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        collections = [
            os.path.join(cnf.coll_folder, i)
            for i in os.listdir(cnf.coll_folder)
            if not i.startswith((".", "_"))
            ]

        ln = len(collections)

        new_images = []
        found_images = []

        for x, collection in enumerate(collections, 1):
            self.__change_live_text(
                    f"{cnf.lang.scaning} "
                    f"{x} "
                    f"{cnf.lang.from_pretext} "
                    f"{ln} "
                    f"{cnf.lang.colls_case}."
                    )

            if not os.path.isdir(collection):
                if collection.endswith(exts):
                    data = (
                        collection,
                        int(os.path.getsize(collection)),
                        int(os.stat(collection).st_birthtime),
                        int(os.stat(collection).st_mtime)
                        )
                    found_images.append(data)

                    if data not in db_images:
                        new_images.append(data)

            for root, dirs, files in os.walk(collection):

                if not cnf.scan_flag:
                    return

                for file in files:

                    if not cnf.scan_flag:
                        return

                    if file.endswith(exts):
                        src = os.path.join(root, file)
                        data = (
                            src,
                            int(os.path.getsize(src)),
                            int(os.stat(src).st_birthtime),
                            int(os.stat(src).st_mtime)
                            )
                        found_images.append(data)

                        if data not in db_images:
                            new_images.append(data)

        if new_images:
            self.need_update = True
            ln = len(new_images)

            values = [
                {
                "b_img150": encode_image(src),
                "b_src": src,
                "b_size": size,
                "b_created": created,
                "b_modified": modified,
                "b_collection": get_coll_name(src),
                "temp": self.__change_live_text(
                        f"{cnf.lang.added} "
                        f"{x} "
                        f"{cnf.lang.from_pretext} "
                        f"{ln} "
                        f"{cnf.lang.new_photo_case}."
                        )
                    }
                for x, (src, size, created, modified) in enumerate(new_images, 1)
                if cnf.scan_flag
                ]

            limit = 300
            values = [
                values[i:i+limit]
                for i in range(0, len(values), limit)
                ]

            for vals in values:
                
                if not cnf.scan_flag:
                    return

                q = sqlalchemy.insert(Thumbs).values(
                    {
                        "img150": sqlalchemy.bindparam("b_img150"),
                        "src": sqlalchemy.bindparam("b_src"),
                        "size": sqlalchemy.bindparam("b_size"),
                        "created": sqlalchemy.bindparam("b_created"),
                        "modified": sqlalchemy.bindparam("b_modified"),
                        "collection": sqlalchemy.bindparam("b_collection")
                        })
                Dbase.conn.execute(q, vals)

        remove_images = []

        for src, size, created, modified in db_images:
            if not cnf.scan_flag:
                return

            if (src, size, created, modified) not in found_images:
                remove_images.append((src, size, created, modified))

        if remove_images:

            self.__change_live_text(cnf.lang.finishing)
            self.need_update = True

            values = [
                {
                "b_src": src,
                "b_size": size,
                "b_created": created,
                "b_modified": modified,
                }
                for src, size, created, modified in remove_images
                if cnf.scan_flag
                ]

            limit = 300
            values = [
                values[i:i+limit]
                for i in range(0, len(values), limit)
                ]

            for vals in values:

                if not cnf.scan_flag:
                    return

                q = sqlalchemy.delete(Thumbs).filter(
                    Thumbs.src == sqlalchemy.bindparam("b_src"),
                    Thumbs.size == sqlalchemy.bindparam("b_size"),
                    Thumbs.created == sqlalchemy.bindparam("b_created"),
                    Thumbs.modified == sqlalchemy.bindparam("b_modified")
                    )
                Dbase.conn.execute(q, vals)


    def __change_live_text(self, text):
        cnf.scan_win_txt = text


scaner = Scaner()