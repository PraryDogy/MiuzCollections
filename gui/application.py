from . import conf, on_exit, tkinter
from .menu import Menu
from .st_bar import StBar
from .thumbnails import Thumbnails
from .widgets import *


class Application:
    def __init__(self):
        conf.root.title(conf.app_name)
        conf.root.configure(bg=conf.bg_color)

        conf.root.createcommand(
            'tk::mac::ReopenApplication', lambda: conf.root.deiconify())

        conf.root.bind('<Command-w>', lambda e: conf.root.iconify())

        if conf.ask_exit:
            conf.root.protocol("WM_DELETE_WINDOW", AskExit)
            conf.root.createcommand("tk::mac::Quit" , AskExit)
        else:
            conf.root.createcommand("tk::mac::Quit" , on_exit)
            conf.root.protocol("WM_DELETE_WINDOW", on_exit)

        CSep(conf.root).pack(fill=tkinter.X, pady=15, padx=(15, 5))

        self.menu = Menu(conf.root)
        self.menu.pack(side=tkinter.LEFT, fill=tkinter.Y, pady=(0, 15))

        right_frame = CFrame(conf.root)
        right_frame.pack(fill=tkinter.BOTH, expand=1)
    
        self.thumbnails = Thumbnails(right_frame)
        self.thumbnails.pack(fill=tkinter.BOTH, expand=1, padx=(15, 5))

        CSep(right_frame).pack(fill=tkinter.X, pady=10, padx=15)

        self.st_bar = StBar(right_frame)
        self.st_bar.pack(pady=(0, 10))

        MacMenu()

        conf.root.eval(f'tk::PlaceWindow {conf.root} center')

        if conf.root_w < 50 or conf.root_h < 50:
            conf.root_w, conf.root_h = 700, 500

        conf.root.geometry(
            (f"{conf.root_w}x{conf.root_h}"
            f"+{conf.root_x}+{conf.root_y}")
            )
        conf.root.minsize(870, 500)


app = Application()