import os
import subprocess
import tkinter

import cfg
from PIL import Image, ImageTk
from Utils import ClipBoard


class Prev:
    def __init__(self, src):
        cfg.ROOT.withdraw()
        newWin = tkinter.Toplevel()
        newWin.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.deiconify())

        newWin.config(bg=cfg.BGCOLOR, padx=15, pady=15)

        if os.path.exists(src):
            self.OpenImg(newWin, src)
        else:
            self.ImgError(newWin)

        self.CopyName(newWin, src)
        self.OpenClose(newWin, src)

        cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')

    
    def OpenImg(self, newWin, src):
        img = Image.open(src)

        w, h = (
            int(cfg.ROOT.winfo_screenwidth()*0.9), 
            int(cfg.ROOT.winfo_screenheight()*0.9)
            )
        img.thumbnail((w, h))

        img = ImageTk.PhotoImage(img)
    
        lbl = tkinter.Label(
            newWin, bg=cfg.BGCOLOR, 
            image=img, compound='center')
        lbl.image = img
        lbl.pack()


    def ImgError(self, newWin):
        txt = (
            'Не могу открыть изображение. Возможные причины:'

            '\n\nНет подключения к сетевому диску MIUZ,'
            '\nпопробуйте открыть любую папку на сетевом диске.'

            '\n\nПопробуйте запустить полное сканирование из настроек.'

            '\n'
            )

        lbl = tkinter.Label(
            newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            text=txt)
        lbl.pack()


    def CopyName(self, newWin, src):

        copyNameFrame = tkinter.Frame(newWin, bg=cfg.BGCOLOR)
        copyNameFrame.pack()

        showPath = tkinter.Label(
            copyNameFrame, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
            pady=15, padx=10, text=src.replace(cfg.PHOTO_DIR, '')
            )
        showPath.pack(side='left')


        def CopyName(label):
            label.config(bg=cfg.BGPRESSED)
            name = src.split('/')[-1].split('.')[0]
            
            ClipBoard.copy(name)
            
            cfg.ROOT.after(
                300, lambda: label.config(bg=cfg.BGBUTTON))
            
            
        copyName = tkinter.Label(
            copyNameFrame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text='Копировать имя файла', padx=10)
        copyName.pack(side='left')           
        copyName.bind('<Button-1>', lambda event: CopyName(copyName))


    def OpenClose(self, newWin, src):
        frame = tkinter.Frame(newWin, bg=cfg.BGCOLOR)
        frame.pack()

        if os.path.exists(src):

            OpenBtn = tkinter.Label(
                frame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
                height=2, width=17, text='Открыть папку')

            OpenBtn.bind(
                '<Button-1>', 
                lambda event: subprocess.check_output(
                    ["/usr/bin/open", '/'.join(src.split('/')[:-1])])
                    )

            OpenBtn.pack(side='left')

        betwBtns = tkinter.Frame(
            frame, bg=cfg.BGCOLOR, width=20)
        betwBtns.pack(side='left')

        closeBtn = tkinter.Label(
            frame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            height=2, width=17, text='Закрыть')

        def close():
            newWin.destroy()
            cfg.ROOT.deiconify()

        closeBtn.bind('<Button-1>', lambda event: close())
        closeBtn.pack(side='left')
