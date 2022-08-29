import os
import subprocess
import tkinter
from Utils.Styled import *

import cfg
from PIL import Image, ImageTk
from Utils.Utils import MyCopy

class Globals:
    src = str()
    
    
class ImageShow(tkinter.Toplevel):
    def __init__(self, src):
        if src is None:
            return
        
        Globals.src = src
        
        tkinter.Toplevel.__init__(self)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", lambda: self.destroy())
        self.bind('<Command-w>', lambda e: self.destroy())
        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        
        if os.path.exists(Globals.src):
            cfg.ROOT.update_idletasks()
            ImageFrame(self)
        else:
            ImageError(self)

        NamePathFrame(self)
        OpenCloseFrame(self)

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.geometry(f'+{self.winfo_x()}+0')
        self.deiconify()


class ImageFrame(MyLabel):
    def __init__(self, master):
        imgSrc = Image.open(Globals.src)
        imgCopy= imgSrc.copy()

        h = int(cfg.ROOT.winfo_screenheight()*0.8)
        w = int(cfg.ROOT.winfo_screenwidth()*0.8)
        imgCopy.thumbnail((w, h))

        imgTk = ImageTk.PhotoImage(imgCopy)

        MyLabel.__init__(self, master, image=imgTk)
        self.image_names = imgTk
        self.pack(expand=True, fill=tkinter.BOTH)


class ImageError(MyLabel):
    def __init__(self, master):
        txt = (
            'Не могу открыть изображение. Возможные причины:'
            '\n\nНет подключения к сетевому диску MIUZ,'
            '\nпопробуйте открыть любую папку на сетевом диске.'
            '\n\nПопробуйте запустить полное сканирование из настроек.'
            )
        MyLabel.__init__(self, master, text=txt)
        self.pack()


class NamePathFrame(MyFrame):
    def __init__(self, master):
        MyFrame.__init__(self, master)
        self.pack(pady=(15, 15))
        NamePathTitle(self)
        NamePathButton(self)
        

class NamePathTitle(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(
            self, master,
            text=Globals.src.replace(cfg.PHOTO_DIR, '')
            )
        self.pack(side=tkinter.LEFT)

          
class NamePathButton(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Копировать имя')        
        self.configure(height=1)
        self.Cmd(lambda e: self.copyToClipboard())
        self.pack(side=tkinter.LEFT, padx=(15, 0))

    def copyToClipboard(self):
        self.Press()
        MyCopy(Globals.src.split('/')[-1].split('.')[0])


class OpenCloseFrame(MyFrame):
    def __init__(self, master):
        MyFrame.__init__(self, master)
        self.pack()
        if os.path.exists(Globals.src):
            OpenButton(self)
        CloseButton(self)


class OpenButton(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Открыть папку')
        self.configure(height=2)
        self.Cmd(lambda e: self.OpenFolder())
        self.pack(side=tkinter.LEFT, padx=(0, 15))
        
    def OpenFolder(self):
        self.Press()
        path = '/'.join(Globals.src.split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])
        

class CloseButton(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.Cmd(lambda e: self.winfo_toplevel().destroy())        
        self.pack(side=tkinter.RIGHT)
