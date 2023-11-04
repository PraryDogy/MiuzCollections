import os
import platform

from cfg import cnf

from .menu import Menu
from .scaner import scaner
from .stbar import StBar
from .thumbnails import Thumbs
from .utils import on_exit, run_applescript, smb_check
from .widgets import *

__all__ = (
    "Application",
    )


class Application:
    def __init__(self):
        if not os.path.exists(os.path.join(cnf.coll_folder, cnf.curr_coll)):
            cnf.curr_coll = cnf.all_colls

        cnf.root.title(cnf.app_name)
        cnf.root.configure(bg=cnf.bg_color)
        cnf.root.createcommand("tk::mac::Quit", on_exit)

        if cnf.root_g["w"] < 50 or cnf.root_g["h"] < 50:
            cnf.root_g["w"], cnf.root_g["h"] = 700, 500

        cnf.root.geometry(
            (f"{cnf.root_g['w']}x{cnf.root_g['h']}"
            f"+{cnf.root_g['x']}+{cnf.root_g['y']}")
            )

        cnf.root.minsize(700, 300)
        cnf.root.deiconify()

        temp = CLabel(
            cnf.root, text=cnf.lng.please_wait,
            font=("San Francisco Pro", 22, "bold")
            )
        temp.pack(expand=1, fill="both")

        mac_ver, _, _ = platform.mac_ver()
        mac_ver = float(".".join(mac_ver.split(".")[:2]))

        if mac_ver > 12:
            cnf.root.bind("<Command-w>", self.minim)
            cnf.root.protocol("WM_DELETE_WINDOW", self.minim)
            cnf.root.createcommand("tk::mac::ReopenApplication", self.maxim)

        else:
            cnf.root.bind("<Command-w>", lambda e: cnf.root.withdraw())
            cnf.root.protocol("WM_DELETE_WINDOW", cnf.root.withdraw)
            cnf.root.createcommand(
                "tk::mac::ReopenApplication", cnf.root.deiconify
                )

        self.menu = Menu(cnf.root)
        r_frame = CFrame(cnf.root)
        self.thumbs = Thumbs(r_frame)
        sep = CSep(r_frame)
        self.stbar = StBar(r_frame)
        MacMenu()

        temp.destroy()
        self.menu.pack(side="left", fill="y")
        r_frame.pack(fill="both", expand=1)
        self.thumbs.pack(fill="both", expand=1)
        sep.pack(fill="x", padx=1, pady=(10, 10))
        self.stbar.pack(pady=(0, 10))

        if smb_check():
            cnf.root.after(1000, scaner.scaner_start)
        else:
            scaner.scaner_sheldue()
            SmbAlert()

        cnf.first_load = False

    def minim(self, e=None):
        applescript = f"""
            set appName to "{cnf.app_name}"
            tell application "System Events"
                set visible of application process appName to false
            end tell
            """

        run_applescript(applescript)

    def maxim(self, e=None):
        applescript = f"""
            set appName to "{cnf.app_name}"
            tell application appName to activate 
            end tell
            """

        run_applescript(applescript)
        cnf.root.focus_force()


app = Application()
