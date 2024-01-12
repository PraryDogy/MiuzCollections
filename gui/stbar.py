import tkinter

from cfg import cnf
from utils import FullScaner, SysUtils

from .scaner_gui import ScanerGui
from .settings import Settings
from .smb_alert import SmbAlert
from .widgets import *

__all__ = ("StBar",)


class Trace:
    settings = None



class StBar(CFrame, SysUtils):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.__stbar = self.__load_stbar()
        self.__stbar.pack(fill="x", expand=1)

    def __load_stbar(self):
        frame = CFrame(master=self)

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        self.sett_btn = CButton(master=frame, text=cnf.lng.settings,
                      width=90, fg_color=cnf.bg_color)
        self.sett_btn.cmd(self.__open_settings)
        self.sett_btn.pack(side="left", padx=(0, 5))

        if Trace.settings:
            cnf.settings_var.trace_remove(mode="read", cbname=Trace.settings)
        Trace.settings = cnf.settings_var.trace_add(
            mode="read", callback=self.setttings_callback)

        self.updating_btn = CButton(master=frame, text=cnf.lng.update,
                                 width=90, fg_color=cnf.bg_color)
        self.updating_btn.cmd(self.__stbar_run_scan)
        self.updating_btn.pack(side="left")

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        default, zoomed = "᎒᎒᎒", "⋮⋮⋮"
        self.grid = CButton(master=frame, text=zoomed if cnf.zoom else default,
                            width=50, fg_color=cnf.bg_color)
        self.grid.pack(side="right", anchor="w", padx=(0, 15))
        self.grid.cmd(lambda e: self.grid_cmd())

        return frame

    def setttings_callback(self, *args):
        if cnf.settings_var.get() == 1:
            self.sett_btn.configure(fg_color=cnf.blue_color)
        else:
            self.sett_btn.configure(fg_color=cnf.bg_color)

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
            if not self.smb_check():
                SmbAlert()
            FullScaner()
        else:
            ScanerGui()
