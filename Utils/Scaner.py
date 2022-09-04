"""

"""

import datetime
import os
import sys

import sqlalchemy

import cfg
from admin import print_alive
from database import Thumbs, Dbase
from utils.utils import create_thumb


class BaseScan(list):
    """
    Looking for folders with year names like "2018", "2020" etc.
    in `cfg.PHOTO_DIR`
    Looking for all folders in year named folders.
    Returns list dirs.

    * param `aged`: bool

    `True` dirs from dirs list with time created earlier than
    `cfg.FILE_AGE` days ago.
    `False` returns dirs list with any time created.

    `cfg.PHOTO_DIR` and `cfg.FILE_AGE` can be changed in
    `cfg.json` (read `cfg.py`) or from app's settings.
    """

    def __init__(self, aged):
        photo_dir = os.path.join(os.sep, *cfg.PHOTO_DIR.split('/'))
        base_dirs = []

        for r in range(2018, datetime.datetime.now().year + 1):
            year_dir = os.path.join(photo_dir, str(r))
            base_dirs.append(year_dir) if os.path.exists(year_dir) else False

        for b_dir in base_dirs:
            for dirs in os.listdir(b_dir):
                self.append(os.path.join(b_dir, dirs))

        self.aged() if aged else False

    def aged(self):
        """
        Removes from dirs list all dirs created earlier than
        `cfg.FILE_AGE` days ago.
        """
        now = datetime.datetime.now().replace(microsecond=0)
        delta = datetime.timedelta(days=int(cfg.FILE_AGE))
        file_age = now - delta

        old_dirs = []
        for dir_item in self:

            birth_float = os.stat(dir_item).st_birthtime
            birth = datetime.datetime.fromtimestamp(birth_float)

            if  birth < file_age:
                old_dirs.append(dir_item)

        [self.remove(o) for o in old_dirs]


class SearchColls(list):
    """
    Looking for folders with `cfg.COLL_FOLDER` name in list of dirs from
    `BaseScan` with `aged=False` param.
    Looking for all folders in `cfg.COLL_FOLDER`
    """
    def __init__(self):

        colls_dirs = list()
        for year_dir in BaseScan(aged=False):
            if os.path.join(os.sep, cfg.COLL_FOLDER) in year_dir:
                colls_dirs.append(year_dir)

        for sub_coll in colls_dirs:
            for i in os.listdir(sub_coll):
                self.append(os.path.join(sub_coll, i))


class SearchRetouched(list):
    """
    Looking for folders with `cfg.RT_FOLDER` name in list of dirs from
    `BaseScan`.

    * param `aged`: bool. Read BaseScan about `aged`.
    """
    def __init__(self, aged):

        for dir_item in BaseScan(aged):
            for root, _, _ in os.walk(dir_item):
                print_alive(sys._getframe().f_code.co_name, root)

                if not cfg.FLAG:
                    return

                if os.path.join(os.sep, cfg.RT_FOLDER) in root:
                    self.append(root)


class SearchImages(list):
    """
    Looking for `.jpeg` files in list of dirs.
    Creates list of tuples with
    `src`, int `size`, int `created`, int `modified`
    """
    def __init__(self, list_dirs):
        all_files = []

        for path in list_dirs:
            for root, _, files in os.walk(path):
                print_alive(sys._getframe().f_code.co_name, root)

                for file in files:
                    all_files.append(os.path.join(root, file))

                    if not cfg.FLAG:
                        return

        jpegs = set()
        for src in all_files:

            if not cfg.FLAG:
                return

            if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                attr = os.stat(src)
                size = int(os.path.getsize(src))
                created = int(props.st_birthtime)
                modified = int(props.st_mtime)
                jpegs.add((src, size, created, modified))

        self.extend(jpegs)


class DbUtils():
    def CollName(self, src):
        """Returns collection name from image path, 
        if collection not detected, collection = noCollection.
        
        Name of collection follows collection folder (cfg.COLL_FOLDER). 
        Path example:
        :path/to/image/cfg.COLL_FOLDER/collection_name

        :param str src: Image path"""

        collName = 'noCollection'
        if f'/{cfg.COLL_FOLDER}' in src:
            collName = src.split(f'/{cfg.COLL_FOLDER}')[-1].split('/')[1]
        return collName

    def InsertRow(self, src, size, birth, mod, coll):
        """Inserts new row in Database > Thumbs. 
        Creates 150, 200, 250, 300 thumbnails from Image's path.
        :param str src: Image's path
        :param int size: Image's size
        :param int birth: Image's date created
        :param int mod: Date last modified of image
        :param str coll: name of collection from CollName mehtod"""

        img150, img200, img250, img300 = create_thumb(src)
        
        values = {
            'img150':img150,
            'img200':img200,
            'img250':img250,
            'img300':img300,
            'src':src,
            'size':size,
            'created':birth,
            'modified':mod,
            'collection':coll
            }

        q = sqlalchemy.insert(Thumbs).values(values)
        Dbase.conn.execute(q)


class DbUpdate(list, DbUtils):
    """
    Gets list of tuples (src, size, created, modified, collection) from
    DataBase > Thumbs.
    Checks whether the list item has been deleted or modified.
    Compares the list with list of tuples from new search.
    Add's to database new item if it's in new search list and not in 
    database list.
    """

    def load_db(self):
        self.clear()
        names =[
            Thumbs.src, Thumbs.size, Thumbs.created,
            Thumbs.modified, Thumbs.collection]
        files = Dbase.conn.execute(sqlalchemy.select(names)).fetchall()
        self.extend(files)

    def Removed(self):
        self.load_db()
        for src, _, _, _, _ in self:
            print_alive(sys._getframe().f_code.co_name, src)

            if not cfg.FLAG:
                return

            if not os.path.exists(src):
                print('removed file', src)

                Dbase.conn.execute(
                    sqlalchemy.delete(Thumbs).where(Thumbs.src==src))

    def Modified(self):
        self.load_db()
        for src, _, _, mod, coll in self:
            atr = os.stat(src)
            if int(atr.st_mtime) > mod:
                print('modified', src)

                nSize = int(os.path.getsize(src))
                nCreated = int(atr.st_birthtime)
                nMod = int(atr.st_mtime)

                Dbase.conn.execute(
                    sqlalchemy.delete(Thumbs).where(Thumbs.src==src))

                coll = self.CollName(src)
                self.InsertRow(src, nSize, nCreated, nMod, coll)

    def Added(self, listDirs):
        self.load_db()
        dbColls = list(
            (size, creat, mod) for _, size, creat, mod, _ in self)

        for src, size, created, mod in listDirs:
            print_alive(sys._getframe().f_code.co_name, src)

            if not cfg.FLAG:
                return

            if (size, created, mod) not in dbColls:
                print('add new file', src)

                coll = self.CollName(src)
                self.InsertRow(src, size, created, mod, coll)
        
    def Moved(self, lisrDirs):
        self.load_db()

        noColls = []
        for src, size, created, mod, coll in self:
            if coll=='noCollection':
                noColls.append((size, created, mod))

        for src, size, created, mod in lisrDirs:
            print_alive(sys._getframe().f_code.co_name, src)

            if not cfg.FLAG:
                return

            if (size, created, mod) in noColls:
                print('moved to colls', src)

                remRow = sqlalchemy.delete(Thumbs).where(
                    Thumbs.size==size,
                    Thumbs.created==created,
                    Thumbs.modified==mod
                    )
                Dbase.conn.execute(remRow)

                coll = self.CollName(src)
                self.InsertRow(src, size, created, mod, coll)
                
    
class UpdateColl():
    def __init__(self):
        cfg.LIVE_LBL.configure(text='10%')
        listDirs = SearchColls()
        images = SearchImages(listDirs)
        
        upd = DbUpdate()
        
        cfg.LIVE_LBL.configure(text='20%')
        upd.Removed()
        
        cfg.LIVE_LBL.configure(text='30%')
        upd.Modified()
        
        cfg.LIVE_LBL.configure(text='40%')
        upd.Added(images)
        
        cfg.LIVE_LBL.configure(text='50%')
        upd.Moved(images)


class UpdateRt():
    def __init__(self, aged=True):
        cfg.LIVE_LBL.configure(text='60%')
        listDirs = SearchRetouched(aged)
        images = SearchImages(listDirs)
        
        upd = DbUpdate()
        
        cfg.LIVE_LBL.configure(text='70%')
        upd.Removed()
        
        cfg.LIVE_LBL.configure(text='80%')
        upd.Modified()
        
        cfg.LIVE_LBL.configure(text='90%')
        upd.Added(images)