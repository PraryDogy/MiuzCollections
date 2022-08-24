import threading
import tkinter

import cfg

from .SplashCmd import Scan, Skip


class Create:
    def __init__(self):
        self.newWin = tkinter.Toplevel()        
        
        cfg.ROOT.eval(f'tk::PlaceWindow {self.newWin} center')

        self.newWin.title('Welcome')
        self.newWin.configure(bg=cfg.BGCOLOR, pady=10)
        self.newWin.resizable(0, 0)

        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', self.newWin.deiconify)

        self.Start()


    def TitleLabel(self):
        title = tkinter.Label(self.newWin, 
            bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            text=f'Сканирую фото за последние {cfg.FILE_AGE} дней')
        title.pack(anchor='center')


    def DynamicLabel(self):
        '''
        return tkinter label object
        '''
        dynamic = tkinter.Label(
            self.newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
            width=40, anchor='center')
        dynamic.pack(anchor='center')
                
        below = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR, height=5)
        below.pack()

        return dynamic


    def SkipBtn(self):
        skipBtn = tkinter.Label(
            self.newWin, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=17, height=2, text='Пропустить')
        
        skipBtn.bind('<Button-1>', lambda event: Skip(self.newWin))
        skipBtn.pack()
        

    def Start(self):        
        self.TitleLabel()
        dynamic = self.DynamicLabel()        
        cfg.LIVE_LBL = dynamic

        self.SkipBtn()

        scanTask = threading.Thread(
            target=lambda: Scan())
        scanTask.start()

        while scanTask.is_alive():
            cfg.ROOT.update()

        self.newWin.destroy()
