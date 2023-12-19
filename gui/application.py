import platform

from cfg import cnf
from utils import SysUtils

from .menu import Menu
from .scaner import scaner
from .smb_alert import SmbAlert
from .stbar import StBar
from .thumbnails import Thumbs
from .topbar import TopBar
from .widgets import *

__all__ = ("Application",)


class Application(SysUtils):
    def __init__(self):
        cnf.root.title(string=cnf.app_name)
        cnf.root.configure(bg=cnf.bg_color)
        cnf.root.createcommand("tk::mac::Quit", self.on_exit)

        if cnf.root_g["w"] < 700 or cnf.root_g["h"] < 300:
            cnf.root_g.update({"w": 700, "h": 300})

        cnf.root.geometry(newGeometry=(f"{cnf.root_g['w']}x{cnf.root_g['h']}"
                                       f"+{cnf.root_g['x']}+{cnf.root_g['y']}"))

        cnf.root.minsize(width=700, height=300)
        cnf.root.deiconify()

        mac_ver, _, _ = platform.mac_ver()
        mac_ver = float(".".join(mac_ver.split(".")[:2]))

        # if mac_ver > 12:
        #     cnf.root.bind_all(sequence="<Command-w>", func=self.minim)
        #     cnf.root.protocol(name="WM_DELETE_WINDOW", func=self.minim)
        #     cnf.root.createcommand("tk::mac::ReopenApplication", self.maxim)

        # else:
        cnf.root.bind_all(sequence="<Command-w>",
                            func=lambda e: cnf.root.withdraw())
        cnf.root.protocol(name="WM_DELETE_WINDOW", func=cnf.root.withdraw)
        cnf.root.createcommand("tk::mac::ReopenApplication", cnf.root.deiconify)

        self.menu = Menu(master=cnf.root)
        menusep = CSep(master=cnf.root, bg="black")

        r_frame = CFrame(master=cnf.root)

        self.topbar = TopBar(master=r_frame)
        self.topbar.pack(fill="x")
        CSep(master=r_frame).pack(fill="x", padx=1, pady=(10, 0))
        self.thumbs = Thumbs(master=r_frame)
        self.thumbs.pack(fill="both", expand=1)
        sep = CSep(master=r_frame)
        sep.pack(fill="x", padx=1)
        self.stbar = StBar(master=r_frame)
        self.stbar.pack(pady=10, fill="x")

        self.menu.pack(side="left", fill="y")
        menusep.pack(side="left", fill="y")
        r_frame.pack(fill="both", expand=1)

        MacMenu()

        if self.smb_check():
            cnf.root.after(ms=100, func=scaner.scaner_start_now)
        else:
            scaner.scaner_sheldue()
            SmbAlert()

    def minim(self, e=None):
        applescript = f"""
            set appName to "{cnf.app_name}"
            tell application "System Events"
                set visible of application process appName to false
            end tell
            """

        self.run_applescript(script=applescript)

    def maxim(self, e=None):
        applescript = f"""
            set appName to "{cnf.app_name}"
            tell application appName to activate 
            end tell
            """

        self.run_applescript(script=applescript)
        cnf.root.focus_force()

app = Application()
