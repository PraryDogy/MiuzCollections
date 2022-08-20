import sqlalchemy

from DataBaseT.models import Config, dBase
from DbUpdate import DbUpdate
from ScanFiles import ScanFiles


class Updater:
    
    def DbExistsModified(self):
        DbUpdate().DbExists()
        DbUpdate().DbModified()


class CollsUpd(Updater):
    '''
    Methods: CollsCurrUpd, CollsUpd
    '''
    def __Update(self, files):
        self.DbExistsModified()
        DbUpdate().DbMovedToColls(files)
        DbUpdate().DbAddNewFile(files)  
 
    def CollsCurrUpd(self):
        self.__Update(ScanFiles().FilesCollCurr())
    
    def CollsUpd(self):
        self.__Update(ScanFiles().FilesColls())
        

class RtUpd(Updater):
    '''
    Methods: RtAgedUpd, RtUpd
    '''
    def __Update(self, files):
        self.DbExistsModified()
        DbUpdate().DbAddNewFile(files)

    def RtAgedUpd(self):
        self.__Update(ScanFiles().FilesRtAged())
        
    def RtUpd(self):
        self.__Update(ScanFiles().FilesRt())


# CollsUpd().CollsUpd()