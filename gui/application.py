from . import conf, on_exit, smb_check, AutoScan
from .menu import Menu
from .st_bar import StBar
from .thumbnails import Thumbnails
from .widgets import *
import subprocess


class Application:
    def __init__(self):
        conf.root.title(conf.app_name)
        conf.root.configure(bg=conf.bg_color)
        conf.root.deiconify()

        conf.root.createcommand(
            'tk::mac::ReopenApplication', conf.root.wm_deiconify)

        conf.root.bind('<Command-w>', self.minim)

        conf.root.createcommand("tk::mac::Quit" , on_exit)
        conf.root.protocol("WM_DELETE_WINDOW", self.minim)

        menu = Menu(conf.root)
        r_frame = CFrame(conf.root)
        thumbnails = Thumbnails(r_frame)
        sep = CSep(r_frame)
        st_bar = StBar(r_frame)

        menu.pack(side="left", fill="y", pady=10)
        r_frame.pack(fill="both", expand=True)
        thumbnails.pack(fill="both", expand=True, padx=10)
        sep.pack(fill="x", pady=10, padx=15)
        st_bar.pack(pady=(0, 10))

        MacMenu()

        if conf.root_w < 50 or conf.root_h < 50:
            conf.root_w, conf.root_h = 700, 500

        conf.root.geometry(
            (f"{conf.root_w}x{conf.root_h}"
            f"+{conf.root_x}+{conf.root_y}")
            )

        conf.root.minsize(870, 500)

        if smb_check():
            AutoScan().auto_scan()
        else:
            SmbAlert()

    def minim(self, e=None):

        args = (
            "-e", f"set tApp to \"{conf.app_name}\"",
            "-e", "tell application \"System Events\" to "
            "set visible of process tApp to false",
            )

        subprocess.call(["osascript", *args])