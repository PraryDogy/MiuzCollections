import datetime
import os
import sys

import sqlalchemy

import cfg
from admin import printAlive
from DataBase.Database import Thumbs, dBase
from Utils.Utils import CreateThumb


class BaseScan(list):    
    def __init__(self, aged=True):
        """List of dirs in folders with 
        year name (year name is 2018, 2020 etc). 
        :param bool aged: if true removes dirs with time created
        earlier than number of days ago (cfg.FILE_AGE)""" 
    
        photoDir = os.path.join(os.sep, *cfg.PHOTO_DIR.split('/')) 
        __baseDirs = list()

        for r in range(2018, datetime.datetime.now().year + 1):
            yearDir = os.path.join(photoDir, str(r))
            __baseDirs.append(yearDir) if os.path.exists(yearDir) else None

        for __b in __baseDirs:
            for dirs in os.listdir(__b):
                self.append(os.path.join(__b, dirs))
    
        self.__aged() if aged else None
    
    def __aged(self):
        now = datetime.datetime.now().replace(microsecond=0)
        delta = datetime.timedelta(days=int(cfg.FILE_AGE))
        fileAge = now - delta
        
        oldDirs = list()
        for s in self:
            
            birthFloat = os.stat(s).st_birthtime
            birth = datetime.datetime.fromtimestamp(birthFloat)

            if  birth < fileAge:
                oldDirs.append(s)                
        
        [self.remove(o) for o in oldDirs]
                  
                    
class SearchColls(list):    
    def __init__(self):
        """List of dirs with cfg.COLL_FOLDER name."""

        collsDirs = list()
        for yearDir in BaseScan(aged=False):
            if f'/{cfg.COLL_FOLDER}' in yearDir:
                collsDirs.append(yearDir)
                
        for subColl in collsDirs:
            for i in os.listdir(subColl):
                self.append(os.path.join(subColl, i))


class SearchRetouched(list):
    def __init__(self, aged=True):
        """List of dirs with "retouch" name (from cfg.RT_FOLDER). 
        :param bool aged: if true scan dirs with time created
        earlier than number of days ago (cfg.FILE_AGE) only.""" 
        
        for dirItem in BaseScan(aged):
            for root, _, _ in os.walk(dirItem):
                printAlive(sys._getframe().f_code.co_name, root)
                
                if not cfg.FLAG:
                    return
                if os.path.join(os.sep, cfg.RT_FOLDER) in root:
                    self.append(root)
                    

class SearchImages(list):
    def __init__(self, listDirs):
        """List of tuples (src, size, created, modified) of jpeg files. 
        :param list lisrDirs: list of dirs for jpeg search."""
        
        allFiles = list()
        
        for path in listDirs:
            for root, _, files in os.walk(path):
                printAlive(sys._getframe().f_code.co_name, root)
                
                for file in files:
                    allFiles.append(os.path.join(root, file))

                    if not cfg.FLAG:
                        return
        
        jpegs = set()
        for src in allFiles:
            
            if not cfg.FLAG:
                return
            if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                props = os.stat(src)                
                size = int(os.path.getsize(src))
                created = int(props.st_birthtime)
                modified = int(props.st_mtime)
                jpegs.add((src, size, created, modified))
                
        self.extend(jpegs)


class DbUtils():
    def CollName(self, src):
        collName = 'noCollection'
        if f'/{cfg.COLL_FOLDER}' in src:
            collName = src.split(f'/{cfg.COLL_FOLDER}')[-1].split('/')[1]
        return collName

    def InsertRow(self, src, size, birth, mod, coll):
        """Input: tuple > (src, size, created, mod, coll). 
        Inserts new row in Database > Files. 
        Requires CreateThumb object."""

        img150, img200, img250, img300 = CreateThumb(src)
        
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
        dBase.conn.execute(q)


class DbUpdate(list, DbUtils):
    def __init__(self):
        names =[
            Thumbs.src, Thumbs.size, Thumbs.created, 
            Thumbs.modified, Thumbs.collection
            ]
        q = sqlalchemy.select(names)
        files = dBase.conn.execute(q).fetchall()  
        self.extend(files)
    
    def Removed(self):
        for src, size, created, mod, coll in self:
            printAlive(sys._getframe().f_code.co_name, src)

            if not cfg.FLAG:
                return
            
            if not os.path.exists(src):
                print('removed file', src)
                
                self.remove((src, size, created, mod, coll))
                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)

    def Modified(self):
        for src, size, created, mod, coll in self:
            atr = os.stat(src)
            if int(atr.st_mtime) > mod:
                print('modified', src)

                nSize = int(os.path.getsize(src))
                nCreated = int(atr.st_birthtime)
                nMod = int(atr.st_mtime)
                
                self.remove((src, size, created, mod, coll))
                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)

                coll = self.CollName(src)
                self.append((src, nSize, nCreated, nMod, coll))                
                self.InsertRow(src, nSize, nCreated, nMod, coll)

    def Added(self, listDirs):
        dbColls = list(
            (size, creat, mod) for src, size, creat, mod, coll in self)

        for src, size, created, mod in listDirs:
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return

            if (size, created, mod) not in dbColls:
                print('add new file', src)

                coll = self.CollName(src)
                self.append((src, size, created, mod, coll))
                self.InsertRow(src, size, created, mod, coll)    
        
    def Moved(self, lisrDirs):
        noColls = list()

        for src, size, created, mod, coll in self:
            if coll=='noCollection':
                noColls.append((size, created, mod))
    
        
        for src, size, created, mod in lisrDirs:
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return
                
            if (size, created, mod) in noColls:
                print('moved to colls', src)
                        
                remRow = sqlalchemy.delete(Thumbs).where(
                    Thumbs.size==size,
                    Thumbs.created==created,
                    Thumbs.modified==mod
                    )
                dBase.conn.execute(remRow)

                coll = self.CollName(src)
                self.InsertRow(src, size, created, mod, coll)
                

class UpdateRt():
    def __init__(self, aged):
        images = SearchImages(SearchRetouched(aged))
        
        upd = DbUpdate()
        upd.Removed()
        upd.Modified()
        upd.Added(images)

class UpdateColl():
    def __init__(self):
        images = SearchImages(SearchColls())
        
        upd = DbUpdate()
        upd.Removed()
        upd.Modified()
        upd.Added(images)
        upd.Moved(images)


UpdateColl()
UpdateRt(aged=True)
