import os
import threading

import cv2
import sqlalchemy

import cfg
from database import Dbase, Thumbs
from utils import get_coll_name, resize_image

__all__ = (
    "scaner"
    )


FLAG = False
DB_IMAGES = []


def insert_row(**kw):
    image = cv2.imread(kw['src'])
    resized = resize_image(image, cfg.THUMB_SIZE, cfg.THUMB_SIZE, True)
    encoded_img = cv2.imencode('.jpg', resized)[1].tobytes()
    values = {
        'img150': encoded_img,
        'src': kw['src'],
        'size': kw['size'],
        'created': kw['birth'],
        'modified': kw['mod'],
        'collection': kw['coll']
        }
    Dbase.conn.execute(sqlalchemy.insert(Thumbs).values(values))



def load_db_images():
    """Returns list of tuples [(`src`, `size`, `created`, `modified`), ...]
    """
    return Dbase.conn.execute(
        sqlalchemy.select(
        Thumbs.src,
        Thumbs.size,
        Thumbs.created,
        Thumbs.modified,
        )
        ).fetchall()


def change_live_lvl(text):
    cfg.LIVE_TEXT = "Обновляю данные:\n" + text


def get_images():
    """
    Looking for `.jpeg` files in list of dirs.
    Creates list of tuples with
    `src`, int `size`, int `created`, int `modified`
    """
    all_files = (
        [
        os.path.join(root, file),
        change_live_lvl(
        f'Сканирую коллекции: {root.replace(cfg.config["COLL_FOLDER"], "Collections")}'
        )
        ]
        for root, _, files in os.walk(cfg.config["COLL_FOLDER"])
        for file in files
        )

    return {
        (
            src,
            int(os.path.getsize(src)),
            int(os.stat(src).st_birthtime),
            int(os.stat(src).st_mtime),
            )
        for src, _ in all_files
        if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG', '.png'))
        }


def removed_images(images_list: list):
    """
    Checks whether each item in the `load_db` list has been
    deleted with os.exists method
    """
    global FLAG

    for src, size, created, mod in load_db_images():
        change_live_lvl(f"Обновляю информацию")

        if (src, size, created, mod) not in images_list:

            path, filename = os.path.split(src)
            change_live_lvl(f"Удаляю: {filename}")
            print('removed file', src)

            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs)
                .where(Thumbs.src == src)
                )

            FLAG = True

def new_images(images_list: list):
    """
    Adds new line with thumnails to database if list item
    not in `load_db` list and exists in `SearchImages` list

    * param `list_dirs`: list of tuples from `SearchImages`
    """
    global FLAG

    for src, size, created, mod in images_list:
        path, filename = os.path.split(src)
        change_live_lvl(f"Ищу новые фото: {filename}")

        if (src, size, created, mod) not in load_db_images():

            print('add new file', src)
            change_live_lvl(f"Добавляю фото: {filename}")

            coll = get_coll_name(src)
            insert_row(
                src = src, size = size, birth = created,mod=mod, coll=coll
                )

            FLAG = True


def update_collections():
    """
    Collection dirs analysis.
    Searchs images.
    Updates the database thumbnails.
    """
    cfg.FLAG = True
    images = get_images()
    removed_images(images)
    new_images(images)
    cfg.FLAG = False
    cfg.LIVE_TEXT = (
    "Created by Evgeny Loshkarev"
    "\nCopyright © 2023 MIUZ Diamonds."
    )

def st_bar_btn(text: str):
    btn = cfg.ST_BAR.winfo_children()[2]
    btn["text"] = text


def scaner():
    global FLAG
    st_bar_btn("Обновление")

    t1 = threading.Thread(target=update_collections, daemon=True)
    t1.start()

    while t1.is_alive():

        cfg.ROOT.update()

        if not cfg.FLAG and FLAG:
            cfg.GALLERY.reload_thumbnails()
            cfg.MENU.reload()
            FLAG = False
            break

    st_bar_btn("Обновить")
