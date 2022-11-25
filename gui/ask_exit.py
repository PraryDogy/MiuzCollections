import tkinter

import cfg
from utils import MyButton, MyFrame, MyLabel, encrypt_cfg, place_center


class AskExit(tkinter.Toplevel):
    def __init__(self, master):
        tkinter.Toplevel.__init__(
            self, master, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: self.on_cancel(self))
        self.bind('<Command-w>', lambda e: self.on_cancel(self))
        self.bind('<Escape>', lambda e: self.on_cancel(self))
        self.bind('<Return>', lambda e: self.on_exit())

        lbl = MyLabel(self, text='Выйти?')
        lbl.pack(pady=(0, 15))

        btns_frame = MyFrame(self)
        btns_frame.pack()
        exit = MyButton(self, text='Выйти')
        exit.cmd(lambda e: self.on_exit())
        cancel = MyButton(self, text='Отмена')
        cancel.cmd(lambda e: self.on_cancel(self))
        [i.configure(height=1, width=11) for i in (exit, cancel)]
        [i.pack(side=tkinter.LEFT, padx=5) for i in (exit, cancel)]

        place_center(self)
        self.deiconify()
        self.grab_set()

    def on_cancel(self, win: tkinter.Toplevel):
        win.destroy()
        cfg.ROOT.focus_force()

    def on_exit(self):
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
        cfg.config['GEOMETRY'] = [w, h, x, y]
        encrypt_cfg(cfg.config)
        cfg.FLAG = False
        quit()