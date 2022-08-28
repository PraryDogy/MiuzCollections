import datetime
import os
import sys

import cfg
import sqlalchemy
from admin import printAlive
from DataBase.Database import Thumbs, dBase

from .Utils import CreateThumb


class BaseScan:
    """Methods: Years, YearsAged""" 
    
    def ScanYears(self):
        """Returns list of dirs. 
        
        Scan cfg.PHOTO_DIR for folders with "year" names, 
        e.g. path/to/photo_dir/2020 and return list of dirs inside each
        "years" folder."""         
           
        yearsDirs = list()
        photoDir = os.path.join(os.sep, *cfg.PHOTO_DIR.split('/')) 

        for i in range(2018, datetime.datetime.now().year + 1):
            yearDir = os.path.join(photoDir, str(i))
            yearsDirs.append(yearDir) if os.path.exists(yearDir) else None

        listDirs = list()
        for year in yearsDirs:
            subDirs = [
                os.path.join(year, subYear) for subYear in os.listdir(year)]
            [listDirs.append(i) for i in subDirs]
        return listDirs

    def ScanYearsAged(self):
        """Returns list of dirs. 
    
        Scan years dirs from Years method for folders 
        younger than date from cfg.FILE_AGE, """
        
        yearsDirs = self.ScanYears()
        agedDirs = list()
        
        fileAge = (
            datetime.datetime.now() - datetime.timedelta(
                days=int(cfg.FILE_AGE)))
        youngerThan = fileAge.timestamp()

        for yearDir in yearsDirs:
            if os.stat(yearDir).st_birthtime > youngerThan:
                agedDirs.append(yearDir)
        return agedDirs


class ScanColls(BaseScan):
    """Inheritance: BaseScan. 
    Methods: ScanColls
    Returns list of dirs."""
    
    def ScanColls(self):
        """Scan years dirs from ScanYears for folders 
        with "Collection" name from cfg.COLL_FOLDER"""
        
        yearsDirs = self.ScanYears()
        collsDirs = list()
        
        for yearDir in yearsDirs:
            if f'/{cfg.COLL_FOLDER}' in yearDir:
                collsDirs.append(yearDir)
                
        allColls = list()
        for subColl in collsDirs:
            for i in os.listdir(subColl):
                allColls.append(os.path.join(subColl, i))
            
        return allColls


class ScanRetouched(BaseScan):
    """Inheritance: BaseScan.
    Methods: ScanRetouched, ScanRetouchedAged.
    Returns list of dirs."""
    
    def __Scan(self, dirsList):
        """Search all folders with cfg.RT_FOLDER name."""
        
        rtDirs = list()
        
        for dirItem in dirsList:
            for root, _, _ in os.walk(dirItem):
                printAlive(sys._getframe().f_code.co_name, root)
                
                if not cfg.FLAG:
                    return
                if os.path.join(os.sep, cfg.RT_FOLDER) in root:
                    rtDirs.append(root)
        return rtDirs
    
    def ScanRetouched(self):
        """Scan years dirs for folders with name from cfg.RT_FOLDER."""
        return self.__Scan(self.ScanYears())
    
    
    def ScanRetouchedAged(self):
        """Scan aged years dirs for folders with name from cfg.RT_FOLDER."""
        return self.__Scan(self.ScanYearsAged())
    

class ScanFiles(ScanRetouched, ScanColls):
    """Inheritance: ScanRetouch, ScanColls.
    Methods: FilesRtAged, FilesRtAll, FilesCollsAll. 
    Returns list of turples: src, int size, int created, int modified."""
    
    def __ScanFiles(self, listDirs):
        """Returns list of jpeg files. 
        Input: list of dirs."""
        
        allFiles = list()
        
        for path in listDirs:
            for root, _, files in os.walk(path):
                printAlive(sys._getframe().f_code.co_name, root)
                
                for file in files:
                    allFiles.append(os.path.join(root, file))

                    if not cfg.FLAG:
                        return
        
        scannedFiles = set()
        for src in allFiles:
            
            if not cfg.FLAG:
                return
            if src.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                props = os.stat(src)                
                size = int(os.path.getsize(src))
                created = int(props.st_birthtime)
                modified = int(props.st_mtime)
                scannedFiles.add((src, size, created, modified))
        return list(scannedFiles)

    def FilesRtAged(self):
        """Scan aged folders with cfg.RT_FOLDER name for jpg files."""
        return self.__ScanFiles(self.ScanRetouchedAged())
    
    def FilesRt(self):
        """Scan folders with cfg.RT_FOLDER name for jpg files."""
        return self.__ScanFiles(self.ScanRetouched())
    
    def FilesColls(self):
        """Scan folders with cfg.COLL_FOLDER name for jpg files."""
        return self.__ScanFiles(self.ScanColls())
    

class DbUtils:
    """Methods: DbLoadColls, InsertRow."""
    
    def DbLoadColls(self):
        """Load Files.src, Files.size, Files.created, Files.modified, 
        Files.collection from Database > Files
        
        Return list of tuples (src, size, created, mod, coll)"""
        
        q = sqlalchemy.select(
            Thumbs.src, 
            Thumbs.size, 
            Thumbs.created, 
            Thumbs.modified, 
            Thumbs.collection
            )
        files = dBase.conn.execute(q).fetchall()    
        return list(tuple(i) for i in files)    


    def InsertRow(self, src, size, created, mod):
        """Input: tuple > (src, size, created, mod, coll). 
        Inserts new row in Database > Files. 
        Requires CreateThumb object."""
        
        collName = 'noCollection'
        if f'/{cfg.COLL_FOLDER}' in src:
            collName = src.split(f'/{cfg.COLL_FOLDER}')[-1].split('/')[1]

        img150, img200, img250, img300 = CreateThumb(src)
        
        q = sqlalchemy.insert(Thumbs).values(
            img150=img150,
            img200=img200,
            img250=img250,
            img300=img300,
            src=src,
            size=size,
            created=created,
            modified=mod,
            collection=collName)
        dBase.conn.execute(q)
            

class DbUpdate(DbUtils):
    """Methods: DbExists, DbModified
    Inheritance: DbUtils"""
    
    def DbExists(self):
        """Get list of dirs from database > Thumbs, 
        check exists with os exitst method. 
        Remove from database if not exists."""
        
        for src, size, created, mod, coll in self.DbLoadColls():
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return
            
            if not os.path.exists(src):
                print('removed file', src)
                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)

    def DbModified(self):
        """Get list items with dirs, modified time of file
        from database > Thumbs. 
        Get modified time of file from dir with os.stat method.
        Compare modified times and replace database row if file from dir
        newer, than in database."""

        for src, size, created, mod, coll in self.DbLoadColls():
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return
            
            fileStat = os.stat(src)
            if int(fileStat.st_mtime) > mod:
                print('modified', src)

                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)
                
                self.InsertRow(
                    src=src, 
                    size=int(os.path.getsize(src)), 
                    created=int(fileStat.st_birthtime), 
                    mod=int(fileStat.st_mtime),
                    )

    def DbAddNewFile(self, scannedFiles):
        """Load items with filesize, file created & file modified from 
        database > Thumbs and compare with scanned files. 
        Add new row if item from scanned files not in dataabase loaded items"""
        
        loadedColls = self.DbLoadColls()
        dbColls = list(
            (size, creat, mod) for src, size, creat, mod, coll in loadedColls
            )

        for src, size, created, mod in scannedFiles:
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return

            if (size, created, mod) not in dbColls:
                print('add new file', src)
                self.InsertRow(src, size, created, mod)    

    def DbMovedToColls(self, scannedColls):
        """!!! Input dirs: scanned collections only. !!!
        
        Load items with filesize, file created, file modified, collection 
        from database > Thumbs. 
        Create list with noCollection only from loaded list tuples.
        Compare collections dirs with created list.
        If dir from collections in noCollection list - update database row
        from noCollection to collection name.
        
        Explanation: if file dir from database with noCollection was found 
        in list of scanned collections, it means that file from noCollection
        was copied to collections folder."""
        
        loadedColls = self.DbLoadColls()

        noColls = list()
        for src, size, created, mod, coll in loadedColls:
            if coll=='noCollection':
                noColls.append((size, created, mod))
    
        
        for src, size, created, mod in scannedColls:
            
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

                self.InsertRow(src, size, created, mod)
                

class CollsUpd(ScanFiles, DbUpdate):
    """Methods: CollsUpd"""
    
    def __Update(self, files):
        """Input: scanned files from FilesScan. 
        Check files from database for existence, modified, 
        add new from scanned files if not in database, 
        change collection if file moved from Retouches to Collections."""
        
        cfg.LIVE_LBL.configure(text='10%')
        self.DbExists()

        cfg.LIVE_LBL.configure(text='20%')
        self.DbModified()
        
        cfg.LIVE_LBL.configure(text='40%')
        self.DbMovedToColls(files)

        cfg.LIVE_LBL.configure(text='50%')
        self.DbAddNewFile(files)  
 
    def CollsUpd(self):
        """Scan folders with 'Collection' name from cfg.COLL_FOLDER for
        jpg files.
        Compare with database.
        Add new, move from noCollection to Collections, remove old, update
        modified."""
        self.__Update(files=self.FilesColls())
        

class RtUpd(ScanFiles, DbUpdate):
    """Methods: RtAgedUpd, RtUpd"""

    def __Update(self, files):
        """Input: scanned files from FilesScan. 
        Check files from database for existence, modified, 
        add new from scanned files if not in database."""

        cfg.LIVE_LBL.configure(text='60%')
        self.DbExists()

        cfg.LIVE_LBL.configure(text='80%')
        self.DbModified()
        
        cfg.LIVE_LBL.configure(text='90%')
        self.DbAddNewFile(files)

    def RtAgedUpd(self):
        """Scan aged folders with 'Retouch' name from cfg.RT_FOLDER for
        jpg files.
        Compare with database.
        Add new, remove old, update modified."""
        
        self.__Update(files=self.FilesRtAged())
        
    def RtUpd(self):
        """Scan all folders with 'Retouch' name from cfg.RT_FOLDER for
        jpg files.
        Compare with database.
        Add new, remove old, update modified."""
        
        txt = (
            'Пожалуйста, подождите. Сканирую фото за все время.'
            )
        
        cfg.LIVE_LBL.configure(text=txt)
        self.__Update(files=self.FilesRt())
