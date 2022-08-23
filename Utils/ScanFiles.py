import datetime
import os
import sys

import cfg
import sqlalchemy
from admin import printAlive
from DataBase.Database import Config, dBase


class ScanYears:
    '''
    Methods: Years, YearsAged
    ''' 
    def Years(self):
        '''
        Returns list of dirs. 
        
        Scan cfg.PHOTO_DIR for folders with "year" names, 
        e.g. path/to/photo_dir/2020 and return list of dirs inside each
        "years" folder.
        '''            
        yearsDirs = list()
        for i in range(2018, datetime.datetime.now().year + 1):
            yearDir = os.path.join(cfg.PHOTO_DIR, str(i))
            yearsDirs.append(yearDir) if os.path.exists(yearDir) else None

        listDirs = list()
        for year in yearsDirs:
            subDirs = [
                os.path.join(year, subYear) for subYear in os.listdir(year)]
            [listDirs.append(i) for i in subDirs]
        return listDirs

    def YearsAged(self):
        '''
        Returns list of dirs. 
    
        Scan years dirs from Years method for folders 
        younger than date from cfg.FILE_AGE, 
        '''
        yearsDirs = self.Years()
        agedDirs = list()
        
        fileAge = (
            datetime.datetime.now() - datetime.timedelta(
                days=int(cfg.FILE_AGE)))
        youngerThan = fileAge.timestamp()

        for yearDir in yearsDirs:
            if os.stat(yearDir).st_birthtime > youngerThan:
                agedDirs.append(yearDir)
        return agedDirs


class ScanColls(ScanYears):
    '''
    Inheritance: ScanYears. 
    Methods: Colls, CollsCurr
    Returns list of dirs. 
    '''
    def Colls(self):
        '''
        Scan years dirs from ScanYears for folders 
        with name from cfg.COLL_FOLDER
        '''
        yearsDirs = self.Years()
        collsDirs = list()
        
        for yearDir in yearsDirs:
            if f'/{cfg.COLL_FOLDER}' in yearDir:
                collsDirs.append(yearDir)
                
        allColls = list()
        for subColl in collsDirs:
            for i in os.listdir(subColl):
                allColls.append(os.path.join(subColl, i))
            
        return allColls


    def CollsCurr(self): 
        '''
        Scan dirs from ScanColls > AllColls for folders
        with name from Database > Config > curColl
        '''
        getCurColl = sqlalchemy.select(Config.value).where(
            Config.name=='currColl')
        currColl = dBase.conn.execute(getCurColl).first()[0]

        return [i for i in self.Colls() if currColl in i]


class ScanRetouched(ScanYears):
    '''
    Inheritance: ScanYears.
    Methods: Retouched, RetouchedAged.
    Returns list of dirs.
    '''
    def __Scan(self, dirsList):
        '''
        Search all folders with cfg.RT_FOLDER name.
        '''
        rtDirs = list()
        
        for dirItem in dirsList:
            for root, _, _ in os.walk(dirItem):
                
                printAlive(sys._getframe().f_code.co_name, root)
                
                if not cfg.FLAG:
                    return
                
                if os.path.join(os.sep, cfg.RT_FOLDER) in root:
                    rtDirs.append(root)
        return rtDirs
    
    def Retouched(self):
        '''
        Scan years dirs for folders with name from cfg.RT_FOLDER.
        '''
        return self.__Scan(self.Years())
    
    
    def RetouchedAged(self):
        '''
        Scan aged month dirs from years for folders 
        with name from cfg.RT_FOLDER.
        '''
        return self.__Scan(self.YearsAged())
    

class ScanFiles(ScanRetouched, ScanColls):
    '''
    Inheritance: ScanRetouch, ScanColls.
    Methods: FilesRtAged, FilesRtAll, FilesCollsAll, FilesCollCurr.
    Returns list of turples: src, int size, int created, int modified.
    '''
    
    def __ScanFiles(self, listDirs):
        
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
        '''
        Scan aged folders with cfg.RT_FOLDER name for jpg files.
        '''
        return self.__ScanFiles(self.RetouchedAged())
    
    
    def FilesRt(self):
        '''
        Scan folders with cfg.RT_FOLDER name for jpg files.
        '''
        return self.__ScanFiles(self.Retouched())
    
    
    def FilesColls(self):
        '''
        Scan folders with cfg.COLL_FOLDER name for jpg files.
        '''
        return self.__ScanFiles(self.Colls())
    
    
    def FilesCollCurr(self):
        '''
        Scan folders with name from 
        Database > Config > currColl for jpg files.
        '''
        return self.__ScanFiles(self.CollsCurr())
