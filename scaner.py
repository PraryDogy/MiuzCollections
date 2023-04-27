import os
import threading

import sqlalchemy

import cfg
from database import Dbase, Thumbs
from utils import encone_image, get_coll_name

__all__ = (
    "scaner"
    )

NEED_UPDATE = False


def change_live_lvl(text):
    cfg.LIVE_TEXT = "Обновляю данные:\n" + text


def st_bar_btn(text: str):
    btn = cfg.ST_BAR.winfo_children()[2]
    btn["text"] = text


def update_collections():
    global NEED_UPDATE

    db_images = (
        Dbase.conn.execute(
        sqlalchemy.select(
        Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified
        ))).fetchall()

    new_images = []
    find_images = []

    for root, dirs, files in os.walk(cfg.config["COLL_FOLDER"]):

        change_live_lvl(root.replace(cfg.config["COLL_FOLDER"], "Collections"))

        for file in files:

            if file.endswith((".jpg", ".JPG", ".jpeg", "JPEG", "png", "PNG")):

                src = os.path.join(root, file)

                data = (
                    src,
                    int(os.path.getsize(src)),
                    int(os.stat(src).st_birthtime),
                    int(os.stat(src).st_mtime)
                    )

                find_images.append(data)

                if data not in db_images:

                    change_live_lvl(f"Новое фото: {file}")
                    new_images.append(data)

    if new_images:

        change_live_lvl("Добавляю новые фото")
        NEED_UPDATE = True

        values = [
            {
            "b_img150": encone_image(src),
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            "b_collection": get_coll_name(src)
            }
            for src, size, created, modified in new_images
            ]

        limit = 300
        values = [values[i:i+limit] for i in range(0, len(values), limit)]

        for vals in values:

            q = (
                sqlalchemy.insert(Thumbs)
                .values(
                    {
                        "img150": sqlalchemy.bindparam("b_img150"),
                        "src": sqlalchemy.bindparam("b_src"),
                        "size": sqlalchemy.bindparam("b_size"),
                        "created": sqlalchemy.bindparam("b_created"),
                        "modified": sqlalchemy.bindparam("b_modified"),
                        "collection": sqlalchemy.bindparam("b_collection")
                        }))

            Dbase.conn.execute(q, vals)

    remove_images = []

    for src, size, created, modified in db_images:
        if (src, size, created, modified) not in find_images:
            path, filename = os.path.split(src)
            change_live_lvl(f"Обновляю фото: {filename}")
            remove_images.append((src, size, created, modified))

    if remove_images:

        change_live_lvl("Завершаю")
        NEED_UPDATE = True

        values = [
            {
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            }
            for src, size, created, modified in remove_images
            ]

        limit = 300
        values = [values[i:i+limit] for i in range(0, len(values), limit)]

        for vals in values:

            q = (
                sqlalchemy.delete(Thumbs)
                .filter(
                    Thumbs.src == sqlalchemy.bindparam("b_src"),
                    Thumbs.size == sqlalchemy.bindparam("b_size"),
                    Thumbs.created == sqlalchemy.bindparam("b_created"),
                    Thumbs.modified == sqlalchemy.bindparam("b_modified"),
                    )
                    )
            Dbase.conn.execute(q, vals)


def scaner():
    global NEED_UPDATE

    cfg.FLAG = True
    st_bar_btn("Обновление")

    t1 = threading.Thread(target=update_collections, daemon=True)
    t1.start()

    while t1.is_alive():
        cfg.ROOT.update()

    if NEED_UPDATE:
        cfg.GALLERY.reload_thumbnails()
        cfg.MENU.reload()
        NEED_UPDATE = False

    cfg.LIVE_TEXT = (
        "Created by Evgeny Loshkarev"
        "\nCopyright © 2023 MIUZ Diamonds."
        )

    st_bar_btn("Обновить")
    cfg.FLAG = False
