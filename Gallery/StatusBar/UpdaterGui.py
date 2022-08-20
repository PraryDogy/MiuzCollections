import threading
import tkinter

import cfg
from Utils.Manage import ReloadGallery

from .UpdaterCmd import UpdateColl, Skip
from SmbChecker.SmbCheck import Check as SmbCheck

def Create():
    if not SmbCheck():
        return
        
    newWin = tkinter.Toplevel(cfg.ROOT, bg=cfg.BGCOLOR, pady=10)
    newWin.attributes('-topmost', 'true')
    newWin.resizable(0,0)
    newWin.title('Обновляю')

    txt=f'Сканирую фото за последние {cfg.FILE_AGE} дней'
    updaterLabel = tkinter.Label(
        newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
        text=txt, width=40, height=1)
    updaterLabel.pack()

    dynamicLabel = tkinter.Label(newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
                                 width=35, height=1, pady=10)
    dynamicLabel.pack()
    cfg.LIVE_LBL = dynamicLabel
    
    skipButton = tkinter.Label(
        newWin, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
        text='Пропустить', width=17, height=2)
    skipButton.pack()        
    skipButton.bind('<Button-1>', lambda event: Skip(newWin))
    
    cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')

    t1 = threading.Thread(target=lambda: UpdateColl())
    t1.start()
    
    while t1.is_alive():
        cfg.ROOT.update()

    ReloadGallery()
    newWin.destroy()
