import os
import platform

from cfg import cnf

from .menu import Menu
from .scaner import scaner
from .stbar import StBar
from .thumbnails import Thumbnails
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
        cnf.root.deiconify()

        cnf.root.createcommand("tk::mac::Quit", on_exit)

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
        self.menu.pack(side="left", fill="y", pady=10)

        r_frame = CFrame(cnf.root)
        r_frame.pack(fill="both", expand=1, padx=15)

        self.thumbnails = Thumbnails(r_frame)
        self.thumbnails.pack(fill="both", expand=1)

        sep = CSep(r_frame)
        sep.pack(fill="x", pady=10)

        self.stbar = StBar(r_frame)
        self.stbar.pack(pady=(0, 10))

        MacMenu()

        if cnf.root_g["w"] < 50 or cnf.root_g["h"] < 50:
            cnf.root_g["w"], cnf.root_g["h"] = 700, 500

        cnf.root.geometry(
            (f"{cnf.root_g['w']}x{cnf.root_g['h']}"
            f"+{cnf.root_g['x']}+{cnf.root_g['y']}")
            )

        cnf.root.minsize(610, 300)

        if smb_check():
            scaner.scaner_start()
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