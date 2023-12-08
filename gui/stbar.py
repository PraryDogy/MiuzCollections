import tkinter

from cfg import cnf
from utils import SysUtils

from .scaner import scaner
from .settings import Settings
from .smb_alert import SmbAlert
from .widgets import *

__all__ = ("StBar",)


class ScanerGui(CWindow, SysUtils):
    def __init__(self):
        CWindow.__init__(self)
        self.title(string=cnf.lng.updating)
        self.geometry(newGeometry="300x90")
        self.place_center(win=self, width=300, height=90)
        self.protocol(name="WM_DELETE_WINDOW", func=self.__close_scangui)
        self.bind(sequence="<Escape>", func=self.__close_scangui)

        self.__live_lbl = CLabel(master=self, text=cnf.scan_win_txt, anchor="w",
                                 justify="left")
        self.__live_lbl.pack(expand=1, fill="both")

        self.__can_btn = CButton(master=self, text=cnf.lng.cancel)
        self.__can_btn.pack(pady=(10, 0))
        self.__can_btn.cmd(self.__cancel_scan)

        self.__live_task = False
        self.__update_livelbl()

        cnf.root.update_idletasks()
        self.grab_set_global()

    def __cancel_scan(self, e: tkinter.Event = None):
        cnf.scan_status = False
        cnf.root.after_cancel(id=self.__live_task)
        self.__live_lbl.configure(text=cnf.lng.please_wait)
        while cnf.scaner_thread.is_alive():
            cnf.root.update()
        self.__close_scangui()

    def __update_livelbl(self):
        if self.winfo_exists():
            self.__live_lbl.configure(text=cnf.scan_win_txt)
            self.__live_task = cnf.root.after(ms=100, func=self.__update_livelbl)

        if not cnf.scan_win_txt:
            cnf.root.after_cancel(id=self.__live_task)
            cnf.root.after(ms=200, func=self.__close_scangui)

    def __close_scangui(self, e: tkinter.Event = None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()


class StBar(CFrame, SysUtils):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.__stbar = self.__load_stbar()
        self.__stbar.pack(fill="x", expand=1)

    def __load_stbar(self):
        frame = CFrame(master=self)

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        btn = CButton(master=frame, text=cnf.lng.settings, width=90)
        btn.cmd(lambda e: self.__open_settings(btn))
        btn.pack(side="left", padx=(0, 20))

        self.stbar_btn = CButton(master=frame, text=cnf.lng.update, width=90)
        if cnf.scan_status:
            self.stbar_btn.configure(text=cnf.lng.updating, fg_color=cnf.blue_color)
        self.stbar_btn.cmd(self.__stbar_run_scan)
        self.stbar_btn.pack(side="left")

        CLabel(master=frame).pack(fill="x", side="left", expand=1)

        info = CButton(master=self, text=cnf.lng.help, fg_color=cnf.bg_color)
        # info.pack(side="right", anchor="w", fill="x")

        # zoomed, default = "⊞", "▦"
        default, zoomed = "᎒᎒᎒", "⋮⋮⋮"
        self.grid = CButton(master=frame, text=zoomed if cnf.zoom else default,
                            fg_color=cnf.bg_color)
        self.grid.pack(side="right", anchor="w")
        self.grid.cmd(lambda e: self.grid_cmd())

        return frame

    def grid_cmd(self):
        cnf.zoom = False if cnf.zoom else True
        # zoomed, default = "⊞", "▦"
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
                scaner.scaner_start_now()
            else:
                scaner.scaner_sheldue()
                SmbAlert()
                return
        else:
            ScanerGui()
