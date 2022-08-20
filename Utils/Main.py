import cfg

from .DbUpdate import DbUpdate
from .ScanFiles import ScanFiles


class Updater:

    def DbExistsModified(self):
        DbUpdate().DbExists()
        DbUpdate().DbModified()


class CollsUpd(Updater):
    '''
    Methods: CollsCurrUpd, CollsUpd
    '''
    def __Update(self, files):
        cfg.LIVE_LBL.config(text='20%')
        self.DbExistsModified()
        
        cfg.LIVE_LBL.config(text='40%')
        DbUpdate().DbMovedToColls(files)

        cfg.LIVE_LBL.config(text='60%')
        DbUpdate().DbAddNewFile(files)  
 
    def CollsCurrUpd(self):
        self.__Update(files=ScanFiles().FilesCollCurr())
    
    def CollsUpd(self):
        self.__Update(files=ScanFiles().FilesColls())
        

class RtUpd(Updater):
    '''
    Methods: RtAgedUpd, RtUpd
    '''
    def __Update(self, files):
        cfg.LIVE_LBL.config(text='80%')
        self.DbExistsModified()

        cfg.LIVE_LBL.config(text='90%')
        DbUpdate().DbAddNewFile(files)

    def RtAgedUpd(self):
        self.__Update(files=ScanFiles().FilesRtAged())
        
    def RtUpd(self):
        txt = (
            'Пожалуйста, подождите. Сканирую фото за все время.'
            )
        
        cfg.LIVE_LBL.config(text=txt)
        self.__Update(files=ScanFiles().FilesRt())


