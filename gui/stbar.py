import tkinter

from cfg import cnf

from .scaner import scaner
from .settings import Settings
from .smb_alert import SmbAlert
from .utils import *
from .widgets import *

__all__ = (
    "StBar",
    )


class ScanerGui(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title(string=cnf.lng.updating)
        self.geometry(newGeometry="300x90")
        place_center(win=self, w=300, h=90)
        self.protocol(name="WM_DELETE_WINDOW", func=self.close_gui)
        self.bind(sequence="<Escape>", func=self.close_gui)

        self.live_lbl = CLabel(master=self, text=cnf.scan_win_txt, anchor="w",
                               justify="left")
        self.live_lbl.pack(expand=1, fill="both")

        self.can_btn = CButton(master=self, text=cnf.lng.cancel)
        self.can_btn.pack(pady=(10, 0))
        self.can_btn.cmd(self.cancel)

        self.live_task = False
        self.update_livelbl()

        cnf.root.update_idletasks()
        self.grab_set_global()

    def cancel(self, e: tkinter.Event = None):
        cnf.scan_flag = False
        cnf.root.after_cancel(id=self.live_task)
        self.live_lbl.configure(text=cnf.lng.please_wait)
        while cnf.scaner_task.is_alive():
            cnf.root.update()
        self.close_gui()

    def update_livelbl(self):
        if self.winfo_exists():
            self.live_lbl.configure(text=cnf.scan_win_txt)
            self.live_task = cnf.root.after(ms=100, func=self.update_livelbl)

        if not cnf.scan_win_txt:
            cnf.root.after_cancel(id=self.live_task)
            cnf.root.after(ms=200, func=self.close_gui)

    def close_gui(self, e: tkinter.Event = None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()


class StBar(CFrame):
    def __init__(self, master):
        CFrame.__init__(self, master=master)

        self.stbar = self.load_stbar()
        self.stbar.pack(fill="x")

    def load_stbar(self):
        frame = CFrame(master=self)

        btn = CButton(master=frame, text=cnf.lng.settings, width=90)
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side="left", padx=(0, 20))

        cnf.stbar_btn = CButton(master=frame, text=cnf.lng.update, width=90)
        cnf.stbar_btn.cmd(self.update_cmd)
        cnf.stbar_btn.pack(side="right")

        return frame

    def reload_stbar(self):
        self.stbar.destroy()
        self.stbar = self.load_stbar()
        self.stbar.pack(fill="x")

    def settings_cmd(self, e: tkinter.Event = None):
        Settings()

    def update_cmd(self, e: tkinter.Event = None):
        if not cnf.scan_flag:
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()
                return
        else:
            ScanerGui()
