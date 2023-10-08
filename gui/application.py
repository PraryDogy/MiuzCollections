from cfg import conf
from .scaner import scaner
from .utils import on_exit, run_applescript, smb_check

from .menu import Menu
from .stbar import StBar
from .thumbnails import Thumbnails
from .widgets import *

__all__ = (
    "Application",
    )


class Application:
    def __init__(self):
        conf.root.title(conf.app_name)
        conf.root.configure(bg=conf.bg_color)
        conf.root.deiconify()

        conf.root.bind('<Command-w>', self.minim)
        conf.root.protocol("WM_DELETE_WINDOW", self.minim)
        conf.root.createcommand("tk::mac::Quit", on_exit)
        # conf.root.createcommand('tk::mac::ReopenApplication', conf.root.deiconify)

        menu = Menu(conf.root)
        r_frame = CFrame(conf.root)
        thumbnails = Thumbnails(r_frame)
        sep = CSep(r_frame)
        stbar = StBar(r_frame)

        menu.pack(side="left", fill="y", pady=10)
        r_frame.pack(fill="both", expand=True)
        thumbnails.pack(fill="both", expand=True, padx=10)
        sep.pack(fill="x", pady=10, padx=15)
        stbar.pack(pady=(0, 10))

        MacMenu()

        if conf.root_w < 50 or conf.root_h < 50:
            conf.root_w, conf.root_h = 700, 500

        conf.root.geometry(
            (f"{conf.root_w}x{conf.root_h}"
            f"+{conf.root_x}+{conf.root_y}")
            )

        conf.root.minsize(870, 500)

        if smb_check():
            scaner.scaner_start()
        else:
            SmbAlert()

    def minim(self, e=None):
        applescript = f"""
            set appName to "{conf.app_name}"
            tell application "System Events"
                set visible of application process appName to false
            end tell
            """

        run_applescript(applescript)

    def maxim(self, e=None):
        applescript = f"""
            set appName to "{conf.app_name}"
            tell application appName to activate 
            end tell
            """

        run_applescript(applescript)
        conf.root.focus_force()