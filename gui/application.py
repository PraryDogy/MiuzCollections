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
            'tk::mac::ReopenApplication', conf.root.deiconify)

        conf.root.bind('<Command-w>', lambda e: conf.root.iconify())

        conf.root.createcommand("tk::mac::Quit" , on_exit)
        conf.root.protocol("WM_DELETE_WINDOW", on_exit)

        # grid.columnconfigure(tuple(range(60)), weight=1)
        # grid.rowconfigure(tuple(range(30)), weight=1)

        sep = CSep(conf.root)
        self.menu = Menu(conf.root)
        self.thumbnails = Thumbnails(conf.root)
        self.st_bar = StBar(conf.root)

        sep.grid(row=0, column=0, pady=15, padx=(15, 5))

        self.menu.grid(row=1, column=0, pady=(0, 15))

        self.thumbnails.grid(row=1, column=1, padx=(15, 5), sticky="nesw")
        sep.grid(row=2, column=1, pady=10, padx=15)
        self.st_bar.grid(row=3, column=1, pady=(0, 10))

        conf.root.rowconfigure((0, 100), weight=100)
        conf.root.columnconfigure((0, 100), weight=100)

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