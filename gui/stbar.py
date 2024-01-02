import tkinter

from cfg import cnf
from utils import SysUtils, Scaner

from .settings import Settings
from .smb_alert import SmbAlert
from .widgets import *

__all__ = ("StBar",)


class StBar(CFrame, SysUtils):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.__stbar = self.__load_stbar()
        self.__stbar.pack(fill="x", expand=1)

    def __load_stbar(self):
        frame = CFrame(master=self)

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        btn = CButton(master=frame, text=cnf.lng.settings, width=100)
        btn.cmd(lambda e: self.__open_settings(btn))
        btn.pack(side="left", padx=(0, 20))

        self.stbar_btn = CButton(master=frame, text=cnf.lng.update, width=100)
        if cnf.scan_status:
            self.stbar_btn.configure(text=cnf.lng.updating, fg_color=cnf.blue_color)
        self.stbar_btn.cmd(self.__stbar_run_scan)
        self.stbar_btn.pack(side="left")

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        default, zoomed = "᎒᎒᎒", "⋮⋮⋮"
        self.grid = CButton(master=frame, text=zoomed if cnf.zoom else default,
                            fg_color=cnf.bg_color)
        self.grid.pack(side="right", anchor="w")
        self.grid.cmd(lambda e: self.grid_cmd())

        return frame

    def grid_cmd(self):
        cnf.zoom = False if cnf.zoom else True
        default, zoomed = "᎒᎒᎒", "⋮⋮⋮"
        self.grid.configure(text=zoomed if cnf.zoom else default)
        cnf.reload_thumbs()

    def reload_stbar(self):
        self.__stbar.destroy()
        self.__stbar = self.__load_stbar()
        self.__stbar.pack(fill="x")

    def __open_settings(self, e: tkinter.Event = None):
        Settings()

    def __stbar_run_scan(self, e: tkinter.Event = None):
        if not cnf.scan_status:
            if self.smb_check():
                Scaner()
            else:
                SmbAlert()
                Scaner()