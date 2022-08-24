import threading

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Utils import *


def OpenCollection(allBtns, currBtn):
    '''
    Change color for all buttons to default.
    Change color for pressed button in thread to prevent gui freezes.
    
    We update database.db > Config table > selectedCollection value to
    name of pressed button, because we create collection buttons with names
    from Thumbs.collection.
    
    Then we destroy and create again image grid. 
    Read Gui > ImgGridPkg > ImgGrid.py notes
    '''
    
    for i in allBtns:
        i.configure(bg=cfg.BGBUTTON)

    t1 = threading.Thread(target=lambda: currBtn.configure(bg=cfg.BGPRESSED))
    t1.start()
    
    updateRow = sqlalchemy.update(Config).where(
            Config.name=='currColl').values(value=currBtn.cget('text'))
    dBase.conn.execute(updateRow)
    
    ReloadGallery()