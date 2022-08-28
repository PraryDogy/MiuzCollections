import tkinter

import cfg

from .Sttngs import Settings


class Create:
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Меню", menu=filemenu)

        filemenu.add_command(
            label='Настройки', command=lambda: Settings())
        filemenu.add_command(label="Поддержка", command=self.Descr)
        filemenu.add_command(label="О программе", command=self.AboutApp)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=cfg.ROOT.destroy)
            
        cfg.ROOT.createcommand(
            'tkAboutDialog', 
            lambda: cfg.ROOT.tk.call('tk::mac::standardAboutPanel'))

        cfg.ROOT.configure(menu=menubar)

    def AboutApp(self):
        newWin = tkinter.Toplevel(
            cfg.ROOT, bg=cfg.BGCOLOR, pady=10, padx=10)
        newWin.withdraw()
        newWin.title('О программе')

        name = (
            f'MiuzGallery {cfg.APP_VER}'
            '\n\n'
            )
        
        made = (
            'Created by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            '\n'
            )

        createdBy = tkinter.Label(
            newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text=name+made)
        createdBy.pack()

        closeButton = tkinter.Label(
            newWin, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            height=2, width=17, text='Закрыть')
        closeButton.bind('<Button-1>', lambda e: newWin.destroy())
        closeButton.pack()
        
        cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')
        newWin.deiconify()
    
    def Descr(self):
        newWin = tkinter.Toplevel(
            cfg.ROOT, bg=cfg.BGCOLOR, pady=10, padx=10)
        newWin.withdraw()
        newWin.title('Поддержка')

        descr = (
            '\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            '\n'
        )

        descrLabel = tkinter.Label(
            newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text=descr)
        descrLabel.pack()

        closeButton = tkinter.Label(
            newWin, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            height=2, width=17, text='Закрыть')
        closeButton.bind('<Button-1>', lambda e: newWin.destroy())
        closeButton.pack()
        
        cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')
        newWin.deiconify()