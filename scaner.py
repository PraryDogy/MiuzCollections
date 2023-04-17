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


def search_images(list_dirs: list):
    """
    Looking for `.jpeg` files in list of dirs.
    Creates list of tuples with
    `src`, int `size`, int `created`, int `modified`
    """
    all_files = []

    for path in list_dirs:
        for root, _, files in os.walk(path):
            for file in files:
                all_files.append(os.path.join(root, file))

    jpegs = set()
    for src in all_files:

        if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
            attr = os.stat(src)
            size = int(os.path.getsize(src))
            created = int(attr.st_birthtime)
            modified = int(attr.st_mtime)
            jpegs.add((src, size, created, modified))

    return list(jpegs)


def db_images():
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
        Thumbs.collection
        )
        ).fetchall()


def removed_images():
    """
    Checks whether each item in the `load_db` list has been
    deleted with os.exists method
    """
    files = db_images()
    for src, _, _, _, _ in files:
        if not os.path.exists(src):
            print('removed file', src)
            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs).where(Thumbs.src==src))


def new_images(list_dirs: list):
    """
    Adds new line with thumnails to database if list item
    not in `load_db` list and exists in `SearchImages` list

    * param `list_dirs`: list of tuples from `SearchImages`
    """
    files = db_images()
    db_colls = list(
        (size, created, mod) for _, size, created, mod, _ in files)
    for src, size, created, mod in list_dirs:
        print_alive(sys._getframe().f_code.co_name, src)

        if (size, created, mod) not in db_colls:
            print('add new file', src)
            # update_livelabel('Добавляю новые фото')
            coll = get_coll_name(src)
            insert_row(src=src, size=size, birth=created,
                            mod=mod, coll=coll)


def update_collections():
    """
    Collection dirs analysis.
    Searchs images.
    Updates the database thumbnails.
    """
    images = search_images(search_collections())
    removed_images()
    new_images(images)


def scaner():
    def __scan():
        """Run Files Scaner & Database Updater from utils"""
        cfg.FLAG = True

        update_collections()

        Dbase.conn.commit()
        cfg.GALLERY.thumbnails_reload()
        cfg.FLAG = False

    cfg.ST_BAR.enable_live_lbl()

    t1 = threading.Thread(target=__scan, daemon=True)
    t1.start()
    while t1.is_alive():
        cfg.ROOT.update()
        if not cfg.FLAG:
            cfg.ROOT.update()
            break
    
    cfg.ST_BAR.disable_live_lbl()