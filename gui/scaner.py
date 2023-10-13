import os

import sqlalchemy

from cfg import conf
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

    def scaner_start(self):
        self.__scaner_cancel()
        self.__scaner()
        ms = conf.autoscan_time*60000
        conf.root.after(ms, self.scaner_start)

    def __scaner_cancel(self):
        conf.flag = False
        if conf.scaner_task:
            while conf.scaner_task.is_alive():
                conf.root.update()
        return True

    def __scaner(self):
        conf.flag = True
        Globals.stbar_btn.configure(
            text=conf.lang.live_updating,
            bg=conf.topbar_color
            )

        task = threading.Thread(target=self.__update_db, daemon=True)
        task.start()
        while task.is_alive():
            conf.root.update()

        self.__change_live_text("")

        if self.need_update:
            Globals.reload_thumbs()
            Globals.reload_menu()
            self.need_update = False

        conf.flag = False
        Globals.stbar_btn.configure(text=conf.lang.upd_btn, bg=conf.btn_color)

    def __update_db(self):
        self.__change_live_text(conf.lang.scaner_prepare)

        db_images = Dbase.conn.execute(
            sqlalchemy.select(
            Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified
            )
            ).fetchall()

        exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

        collections = [
            os.path.join(conf.coll_folder, i)
            for i in os.listdir(conf.coll_folder)
            if not i.startswith((".", "_"))
            ]

        ln = len(collections)

        new_images = []
        found_images = []

        for x, collection in enumerate(collections, 1):
            self.__change_live_text(
                    f"{conf.lang.live_scan} "
                    f"{x} "
                    f"{conf.lang.live_from} "
                    f"{ln} "
                    f"{conf.lang.live_collections}."
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

                if not conf.flag:
                    return

                for file in files:

                    if not conf.flag:
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
                        f"{conf.lang.live_added} "
                        f"{x} "
                        f"{conf.lang.live_from} "
                        f"{ln} "
                        f"{conf.lang.live_newphoto}."
                        )
                    }
                for x, (src, size, created, modified) in enumerate(new_images, 1)
                if conf.flag
                ]

            limit = 300
            values = [
                values[i:i+limit]
                for i in range(0, len(values), limit)
                ]

            for vals in values:
                
                if not conf.flag:
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
            if not conf.flag:
                return

            if (src, size, created, modified) not in found_images:
                remove_images.append((src, size, created, modified))

        if remove_images:

            self.__change_live_text(conf.lang.live_finish)
            self.need_update = True

            values = [
                {
                "b_src": src,
                "b_size": size,
                "b_created": created,
                "b_modified": modified,
                }
                for src, size, created, modified in remove_images
                if conf.flag
                ]

            limit = 300
            values = [
                values[i:i+limit]
                for i in range(0, len(values), limit)
                ]

            for vals in values:

                if not conf.flag:
                    return

                q = sqlalchemy.delete(Thumbs).filter(
                    Thumbs.src == sqlalchemy.bindparam("b_src"),
                    Thumbs.size == sqlalchemy.bindparam("b_size"),
                    Thumbs.created == sqlalchemy.bindparam("b_created"),
                    Thumbs.modified == sqlalchemy.bindparam("b_modified")
                    )
                Dbase.conn.execute(q, vals)


    def __change_live_text(self, text):
        conf.live_text = text


scaner = Scaner()