import tkinter

import cfg
from utils import MyButton, MyFrame, MyLabel, encrypt_cfg, place_center


class AskExit(tkinter.Toplevel):
    def __init__(self, master):
        tkinter.Toplevel.__init__(
            self, master, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: self.on_cancel())
        self.bind('<Command-w>', lambda e: self.on_cancel())
        self.bind('<Escape>', lambda e: self.on_cancel())

        lbl = MyLabel(self, text='Выйти?')

        btns_frame = MyFrame(self)

        exit = MyButton(self, text='Выйти')
        exit.cmd(lambda e: self.on_exit())
        exit.configure(height=1, width=11)

        cancel = MyButton(self, text='Отмена')
        cancel.cmd(lambda e: self.on_cancel())
        cancel.configure(height=1, width=11)

        lbl.pack(pady=(0, 15))
        exit.pack(side=tkinter.LEFT, padx=(0, 10))
        cancel.pack(side=tkinter.RIGHT)
        btns_frame.pack()

        place_center(self)
        self.deiconify()
        self.grab_set()

    def on_cancel(self):
        self.destroy()
        cfg.ROOT.focus_force()

    def on_exit(self):
        cfg.FLAG = False

        cfg.ROOT.update_idletasks()
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()

        cfg.config['ROOT_SIZE'] = f'{w}x{h}'
        cfg.config['ROOT_POS'] = f'+{x}+{y}'

        encrypt_cfg(cfg.config)
        quit()