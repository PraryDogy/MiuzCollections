import os
import sys
import threading

import cv2
import sqlalchemy

import cfg
from admin import print_alive
from database import Dbase, Thumbs
from utils import get_coll_name, resize_image


FLAG = False

def insert_row(**kw):
    """
    Adds new line to Database > Thumbs with new thumbnails.
    Creates thumbnails with `create_thumb` method from `utils`
    * param `src`: Image's path
    * param `size`: Image's size `int`
    * param `birth`: Image's date created `int`
    * param `mod`: Date last modified of image `int`
    * param `coll`: name of collection created with `get_coll_name`
    """
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
        change_live_lvl(root)
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


def removed_images(images_list: list):
    """
    Checks whether each item in the `load_db` list has been
    deleted with os.exists method
    """
    global FLAG

    for data in load_db_images():
        if data not in images_list:

            change_live_lvl("Удаляю лишнее")
            print('removed file', data[0])

            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs)
                .where(Thumbs.src==data[0])
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

        if (src, size, created, mod) not in load_db_images():
            print('add new file', src)
            change_live_lvl("Добавляю новые фото")

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
    "MiuzPhoto. Created by Evgeny Loshkarev"
    "\nCopyright © 2023 MIUZ Diamonds. All rights reserved."
    )


def scaner():
    global FLAG
    cfg.ST_BAR.enable_live_lbl()

    t1 = threading.Thread(target=update_collections, daemon=True)
    t1.start()

    while t1.is_alive():

        cfg.ROOT.update()

        if not cfg.FLAG and FLAG:
            cfg.GALLERY.reload_thumbs()
            FLAG = False
            break

    cfg.GALLERY.reload_menu()
    cfg.ST_BAR.disable_live_lbl()
