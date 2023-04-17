import os
import sys
import threading

import cv2
import sqlalchemy

import cfg
from admin import print_alive
from database import Dbase, Thumbs
from utils import get_coll_name, resize_image


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
        'src':kw['src'],
        'size':kw['size'],
        'created':kw['birth'],
        'modified':kw['mod'],
        'collection':kw['coll']}
    Dbase.conn.execute(sqlalchemy.insert(Thumbs).values(values))


def search_collections():
    """
    Returns list of dirs.
    Looking for all folders in `cfg.COLL_FOLDER`
    """
    return (
        os.path.join(cfg.config['COLL_FOLDER'], i)
        for i in os.listdir(cfg.config['COLL_FOLDER'])
        )


def get_images(list_dirs: list):
    """
    Looking for `.jpeg` files in list of dirs.
    Creates list of tuples with
    `src`, int `size`, int `created`, int `modified`
    """
    all_files = [
        os.path.join(root, file)

        for collection in list_dirs
        for root, _, files in os.walk(collection)
        for file in files
        ]

    return {
        (
            src,
            int(os.path.getsize(src)),
            int(os.stat(src).st_birthtime),
            int(os.stat(src).st_mtime),
            )
        for src in all_files
        if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG', '.png'))
        }


def load_db_images():
    """
    Loads from Database > Thumbs: `src`, `size`, `created`,
    `modified`, `collection` to tuples list
    """
    return Dbase.conn.execute(
        sqlalchemy.select(
        Thumbs.src,
        Thumbs.size,
        Thumbs.created,
        Thumbs.modified,
        )
        ).fetchall()


def removed_images():
    """
    Checks whether each item in the `load_db` list has been
    deleted with os.exists method
    """
    for data in load_db_images():
        if not os.path.exists(data[0]):
            print('removed file', data[0])
            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs)
                .where(Thumbs.src==data[0])
                )


def new_images(images_list: list):
    """
    Adds new line with thumnails to database if list item
    not in `load_db` list and exists in `SearchImages` list

    * param `list_dirs`: list of tuples from `SearchImages`
    """
    for src, size, created, mod in images_list:

        if (src, size, created, mod) not in load_db_images():
            print('add new file', src)

            coll = get_coll_name(src)
            insert_row(
                src = src, size = size, birth = created,mod=mod, coll=coll
                )


def update_collections():
    """
    Collection dirs analysis.
    Searchs images.
    Updates the database thumbnails.
    """
    cfg.FLAG = True
    collections_dirs = search_collections()
    images = get_images(collections_dirs)
    removed_images()
    new_images(images)
    cfg.FLAG = False


def scaner():
    cfg.ST_BAR.enable_live_lbl()

    t1 = threading.Thread(target=update_collections, daemon=True)
    t1.start()

    while t1.is_alive():

        cfg.ROOT.update()

        if not cfg.FLAG:
            cfg.GALLERY.thumbnails_reload()
            break

    cfg.ST_BAR.disable_live_lbl()