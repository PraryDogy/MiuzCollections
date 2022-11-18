"""

"""

import datetime
import os
import sys
import threading

import cfg
import sqlalchemy
from admin import print_alive
from database import Dbase, Thumbs
from gui.smb_checker import SmbChecker
from utils import create_thumb, encrypt_cfg, get_coll_name, smb_check
import tkinter

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
    img150 = create_thumb(kw['src'])[0]
    values = {
        'img150': img150, 
        'src':kw['src'], 'size':kw['size'],
        'created':kw['birth'], 'modified':kw['mod'],
        'collection':kw['coll']}
    Dbase.conn.execute(sqlalchemy.insert(Thumbs).values(values))


def search_years():
    """
    Returns list dirs.
    Looking for folders with year names like "2018", "2020" etc.
    in `cfg.PHOTO_DIR`
    Looking for all folders in year named folders.
    """
    photo_dir = os.path.join(os.sep, *cfg.config['PHOTO_DIR'].split('/'))
    base_dirs = []
    for r in range(2018, datetime.datetime.now().year + 1):
        year_dir = os.path.join(photo_dir, str(r))
        base_dirs.append(year_dir) if os.path.exists(year_dir) else False
    years_dirs = []
    for b_dir in base_dirs:
        for dirs in os.listdir(b_dir):
            years_dirs.append(os.path.join(b_dir, dirs))
    return years_dirs


def search_aged_years(list_dirs: list):
    """
    Returns list of dirs.
    Looking for all dirs created later than `cfg.FILE_AGE` days ago

    * param `list_dirs`: list of path like objects
    """
    now = datetime.datetime.now().replace(microsecond=0)
    delta = datetime.timedelta(days=int(cfg.config['FILE_AGE']))
    file_age = now - delta
    aged_years = []
    for dir_item in list_dirs:
        birth_float = os.stat(dir_item).st_birthtime
        birth = datetime.datetime.fromtimestamp(birth_float)
        if  birth > file_age:
            aged_years.append(dir_item)
    return aged_years


def search_collections():
    """
    Returns list of dirs.
    Looking for all folders in `cfg.COLL_FOLDER`
    """
    colls = []
    for sub_coll in os.listdir(cfg.config['COLL_FOLDER']):
        colls.append(os.path.join(cfg.config['COLL_FOLDER'], sub_coll))
    return colls


def search_retouched(list_dirs: list):
    """
    Returns list of dirs.
    Looking for folders with `cfg.RT_FOLDER` name in list of dirs

    * param `list_dirs`: list of path like objects
    """
    retouched = []
    for dir_item in list_dirs:
        for root, _, _ in os.walk(dir_item):
            print_alive(sys._getframe().f_code.co_name, root)
            if os.path.join(os.sep, cfg.config['RT_FOLDER']) in root:
                retouched.append(root)
    return retouched


def search_images(list_dirs: list):
    """
    Looking for `.jpeg` files in list of dirs.
    Creates list of tuples with
    `src`, int `size`, int `created`, int `modified`
    """
    all_files = []
    for path in list_dirs:
        for root, _, files in os.walk(path):
            print_alive(sys._getframe().f_code.co_name, root)
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
    names =[
        Thumbs.src, Thumbs.size, Thumbs.created,
        Thumbs.modified, Thumbs.collection]
    return Dbase.conn.execute(sqlalchemy.select(names)).fetchall()


def removed_images():
    """
    Checks whether each item in the `load_db` list has been
    deleted with os.exists method
    """
    files = db_images()
    for src, _, _, _, _ in files:
        print_alive(sys._getframe().f_code.co_name, src)
        if not os.path.exists(src):
            print('removed file', src)
            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs).where(Thumbs.src==src))


def modified_images():
    """
    Checks whether each item in the `load_db` list has been 
    modified by comparing file modification dates
    """
    files = db_images()
    for src, _, _, mod, coll in files:
        atr = os.stat(src)
        if int(atr.st_mtime) > mod:
            print('modified', src)
            n_size = int(os.path.getsize(src))
            n_birth = int(atr.st_birthtime)
            n_mod = int(atr.st_mtime)
            Dbase.conn.execute(
                sqlalchemy.delete(Thumbs).where(Thumbs.src==src))
            coll = get_coll_name(src)
            insert_row(src=src, size=n_size, birth=n_birth,
                        mod=n_mod, coll=coll)


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
            coll = get_coll_name(src)
            insert_row(src=src, size=size, birth=created,
                            mod=mod, coll=coll)


def moved_images(list_dirs: list):
    """
    Updates database line if list item is in both lists (`db_load`,
    `SearchImages`).
    It's means, that image was copied or moved to `collections` folder.

    We have only two places where we search images: folders with
    `cfg.RT_FOLDER` name and collection folders with `cfg.COLL_FOLDER`.
    Folder with collection name is a priority.
    If image in both folder, in database will only one line about this
    image - from collection folder.

    * param `list_dirs`: list of tuples from `SearchImages`
    """
    files = db_images()
    no_colls = []
    for src, size, created, mod, coll in files:
        if coll=='Без коллекций':
            no_colls.append((size, created, mod))
    for src, size, created, mod in list_dirs:
        print_alive(sys._getframe().f_code.co_name, src)

        if (size, created, mod) in no_colls:
            print('moved to colls', src)
            Dbase.conn.execute(sqlalchemy.delete(Thumbs).where(
                Thumbs.size==size, Thumbs.created==created,
                Thumbs.modified==mod))
            coll = get_coll_name(src)
            insert_row(src=src, size=size, birth=created,
                            mod=mod, coll=coll)


def update_livelabel(percent: str):
    try:
        cfg.LIVE_LBL['text'] = f'Обновление {percent}%'
    except tkinter.TclError:
        print('livelabel was destroyed')


def update_collections():
    """
    Collection dirs analysis.
    Searchs images.
    Updates the database thumbnails.
    """
    cfg.LIVE_LBL['fg'] = cfg.FONTCOLOR
    update_livelabel('10')
    images = search_images(search_collections())
    update_livelabel('20')
    removed_images()
    update_livelabel('30')
    modified_images()
    update_livelabel('40')
    new_images(images)
    update_livelabel('50')
    moved_images(images)


def update_nocollection(aged: bool):
    """
    Collection dirs analysis.
    Searchs images.
    Updates database thumbnails.

    * param `aged`: true = updates dirs created later
    than `cfg.FILE_AGE` value
    """
    update_livelabel('60')
    if aged:
        aged_years = search_aged_years(search_years())
        aged_dirs = search_retouched(aged_years)
    else:
        aged_dirs = search_retouched(search_years())
    images = search_images(aged_dirs)
    update_livelabel('70')
    removed_images()
    update_livelabel('80')
    modified_images()
    update_livelabel('90')
    new_images(images)
    try:
        cfg.LIVE_LBL['fg'] = cfg.BGCOLOR
    except tkinter.TclError:
        print('livelabel was destroyed')


def scaner():
    if not smb_check():
        SmbChecker()
        return

    def __scan():
        """Run Files Scaner & Database Updater from utils"""
        update_collections()
        if cfg.config['TYPE_SCAN'] == 'full':
            cfg.config['TYPE_SCAN'] = ''
            encrypt_cfg(cfg.config)
            update_nocollection(aged=False)
        else:
            update_nocollection(aged=True)
        Dbase.conn.execute('VACUUM')
        try:
            cfg.THUMBNAILS_RELOAD()
        except Exception:
            print('images_reset error')
            cfg.THUMBNAILS_RELOAD()
    t1 = threading.Thread(target=__scan, daemon=True)
    t1.start()
    while t1.is_alive():
        cfg.ROOT.update()