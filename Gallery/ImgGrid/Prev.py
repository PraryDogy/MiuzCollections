import os
import subprocess
import tkinter

import cfg
from PIL import Image, ImageTk
# from Utils.Utils import *


class Prev:
    def __init__(self, src):
        if src is None:
            return
        
        self.src = src
        self.newWin = tkinter.Toplevel()
        self.newWin.protocol("WM_DELETE_WINDOW", lambda: self.newWin.destroy())

        self.newWin.configure(bg=cfg.BGCOLOR, padx=15, pady=15)

        copyName = self.CopyName()
        openClose = self.OpenClose()
        
        if os.path.exists(self.src):
            cfg.ROOT.update_idletasks()
            h = copyName.winfo_reqheight() + openClose.winfo_height()
            openImg = self.OpenImg(h)
        else:
            openImg = self.ImgError()

        for i in [openImg, copyName, openClose]:
            i.pack()

        cfg.ROOT.eval(f'tk::PlaceWindow {self.newWin} center')
        self.newWin.geometry(f'+{self.newWin.winfo_x()}+0')
    
    def OpenImg(self, h):
        frame = tkinter.Frame(self.newWin, bg='black')

        imgSrc = Image.open(self.src)
        imgCopy= imgSrc.copy()

        h = int(cfg.ROOT.winfo_screenheight()*0.8)-h
        w = int(cfg.ROOT.winfo_screenwidth()*0.8)
        imgCopy.thumbnail((w, h))

        imgTk = ImageTk.PhotoImage(imgCopy)
        label = tkinter.Label(frame, image=imgTk, bg=cfg.BGCOLOR)
        label.pack(fill='both', expand=True)
        label.image = imgTk

        return frame


    def ImgError(self):
        txt = (
            'Не могу открыть изображение. Возможные причины:'
            '\n\nНет подключения к сетевому диску MIUZ,'
            '\nпопробуйте открыть любую папку на сетевом диске.'
            '\n\nПопробуйте запустить полное сканирование из настроек.'
            '\n'
            )

        label = tkinter.Label(
            self.newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            text=txt)
        return label


    def CopyName(self):
        frame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)

        showPath = tkinter.Label(
            frame, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
            pady=15, padx=10, text=self.src.replace(cfg.PHOTO_DIR, '')
            )
        showPath.pack(side='left')
                        
        self.copyName = tkinter.Label(
            frame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text='Копировать имя файла', padx=10)
        self.copyName.pack(side='left')           
        self.copyName.bind('<Button-1>', lambda event: self.copyToClipboard())
        return frame


    def copyToClipboard(self):
        self.copyName.configure(bg=cfg.BGPRESSED)
        name = self.src.split('/')[-1].split('.')[0]
        # MyCopy(name)
        cfg.ROOT.after(
            300, lambda: self.copyName.configure(bg=cfg.BGBUTTON))


    def OpenClose(self):
        frame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)

        if os.path.exists(self.src):
            OpenBtn = tkinter.Label(
                frame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
                height=2, width=17, text='Открыть папку')
            OpenBtn.bind(
                '<Button-1>', 
                lambda event: subprocess.check_output(
                    ["/usr/bin/open", '/'.join(self.src.split('/')[:-1])])
                    )
            OpenBtn.pack(side='left')

        betwBtns = tkinter.Frame(
            frame, bg=cfg.BGCOLOR, width=20)
        betwBtns.pack(side='left')

        closeBtn = tkinter.Label(
            frame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            height=2, width=17, text='Закрыть')

        closeBtn.bind('<Button-1>', lambda event: self.newWin.destroy())
        closeBtn.pack(side='left')
        return frame
