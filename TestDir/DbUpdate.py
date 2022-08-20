import os
import sys

import cfg
import sqlalchemy
from admin import printAlive
from DataBase.Database import Thumbs, dBase

from .CreateThumb import Create as CreateThumb


class DbUtils:
    '''
    Methods: DbLoadColls, InsertRow.
    '''
    def DbLoadColls(self):
        '''
        Load Files.src, Files.size, Files.created, Files.modified, 
        Files.collection from Database > Files
        
        Return list of tuples (src, size, created, mod, coll)
        '''
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
        '''
        Input: tuple > (src, size, created, mod, coll). 
        Inserts new row in Database > Files. 
        Requires CreateThumb object.
        '''
        
        collName = 'noCollection'
        if f'/{cfg.COLL_FOLDER}' in src:
            collName = src.split(f'/{cfg.COLL_FOLDER}')[-1].split('/')[1]

        img150, img200, img250, img300 = CreateThumb(src).resized
        
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
    def DbExists(self):
        for src, size, created, mod, coll in self.DbLoadColls():
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return
            
            if not os.path.exists(src):
                
                print('removed file')
                print(src)
                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)

    def DbModified(self):
        for src, size, created, mod, coll in self.DbLoadColls():
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return
            
            fileStat = os.stat(src)
            if int(fileStat.st_mtime) > mod:
                
                print('modified')
                print(src)
                
                q = sqlalchemy.delete(Thumbs).where(Thumbs.src==src)
                dBase.conn.execute(q)
                
                self.InsertRow(
                    src=src, 
                    size=int(os.path.getsize(src)), 
                    created=int(fileStat.st_birthtime), 
                    mod=int(fileStat.st_mtime),
                    )

    def DbAddNewFile(self, scannedFiles):
        loadedColls = self.DbLoadColls()
        dbColls = list(
            (size, creat, mod) for src, size, creat, mod, coll in loadedColls
            )

        for src, size, created, mod in scannedFiles:
            
            printAlive(sys._getframe().f_code.co_name, src)
            
            if not cfg.FLAG:
                return

            if (size, created, mod) not in dbColls:
                print('add new file')
                self.InsertRow(src, size, created, mod)
    

    def DbMovedToColls(self, scannedColls):
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
                
                print('moved to colls')
                print(src)

                remRow = sqlalchemy.delete(Thumbs).where(
                    Thumbs.size==size,
                    Thumbs.created==created,
                    Thumbs.modified==mod
                )
                dBase.conn.execute(remRow)

                self.InsertRow(src, size, created, mod)


