import os
import threading

import sqlalchemy

import cfg
from database import Dbase, Thumbs
from utils import encode_image, get_coll_name

__all__ = (
    "scaner",
    )

UPDATE_THUMBNAILS = False


def change_live_lvl(text):
    cfg.LIVE_TEXT = text


def st_bar_btn(text: str, color: str):
    btn = cfg.ST_BAR.winfo_children()[2]
    btn["text"] = text
    btn["bg"] = color


def update_collections():
    global UPDATE_THUMBNAILS

    db_images = Dbase.conn.execute(
        sqlalchemy.select(
        Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified
        )
        ).fetchall()

    exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

    collections = [
        os.path.join(cfg.config["COLL_FOLDER"], i)
        for i in os.listdir(cfg.config["COLL_FOLDER"])
        if not i.startswith(".")
        ]

    ln = len(collections)

    new_images = []
    found_images = []

    for x, collection in enumerate(collections, 1):
        change_live_lvl(f"Сканирую {x} из {ln} коллекций.")

        for root, dirs, files in os.walk(collection):

            if not cfg.FLAG:
                return

            for file in files:

                if not cfg.FLAG:
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
        UPDATE_THUMBNAILS = True
        ln = len(new_images)

        values = [
            {
            "b_img150": encode_image(src),
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            "b_collection": get_coll_name(src),
            "temp": change_live_lvl(
                f"Добавлено {x} из {ln} новых фото."
                )
                }
            for x, (src, size, created, modified) in enumerate(new_images)
            if cfg.FLAG
            ]

        limit = 300
        values = [
            values[i:i+limit]
            for i in range(0, len(values), limit)
            ]

        for vals in values:
            
            if not cfg.FLAG:
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
        if not cfg.FLAG:
            return

        if (src, size, created, modified) not in found_images:
            remove_images.append((src, size, created, modified))

    if remove_images:

        change_live_lvl("Завершаю")
        UPDATE_THUMBNAILS = True

        values = [
            {
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            }
            for src, size, created, modified in remove_images
            if cfg.FLAG
            ]

        limit = 300
        values = [
            values[i:i+limit]
            for i in range(0, len(values), limit)
            ]

        for vals in values:

            if not cfg.FLAG:
                return

            q = sqlalchemy.delete(Thumbs).filter(
                Thumbs.src == sqlalchemy.bindparam("b_src"),
                Thumbs.size == sqlalchemy.bindparam("b_size"),
                Thumbs.created == sqlalchemy.bindparam("b_created"),
                Thumbs.modified == sqlalchemy.bindparam("b_modified")
                )
            Dbase.conn.execute(q, vals)


def scaner():
    global UPDATE_THUMBNAILS

    cfg.FLAG = True
    st_bar_btn("Обновление", cfg.SELECTED)

    cfg.SCANER_TASK = threading.Thread(target = update_collections, daemon = True)
    cfg.SCANER_TASK.start()

    while cfg.SCANER_TASK.is_alive():
        cfg.ROOT.update()

    cfg.LIVE_TEXT = ""

    if UPDATE_THUMBNAILS:
        cfg.THUMBNAILS.reload_thumbnails()
        cfg.MENU.reload()
        UPDATE_THUMBNAILS = False

    cfg.FLAG = False
    st_bar_btn("Обновить", cfg.BUTTON)
