import tkinter

from cfg import cnf
from .scaner import scaner
from .utils import *

from .globals import Globals
from .settings import Settings
from .widgets import *

__all__ = (
    "StBar",
    )


class ScanerGui(CWindow):
    def __init__(self):
        super().__init__()
        self.title(cnf.lng.updating)
        self.geometry("300x90")

        self.live_lbl = CLabel(
            self,
            text = cnf.scan_win_txt,
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            )
        self.live_lbl.pack(expand=True, fill="both")

        self.can_btn = CButton(self, text=cnf.lng.cancel)
        self.can_btn.pack(pady=(10, 0))
        self.can_btn.cmd(self.cancel)

        cnf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.live_task = False
        self.update_livelbl()

    def cancel(self, e=None):
        cnf.scan_flag = False
        cnf.root.after_cancel(self.live_task)
        self.live_lbl.configure(text=cnf.lng.please_wait)
        while cnf.scaner_task.is_alive():
            cnf.root.update()
        self.destroy()
        focus_last_win()

    def update_livelbl(self):

        if self.winfo_exists():
            self.live_lbl["text"] = cnf.scan_win_txt
            self.live_task = cnf.root.after(100, self.update_livelbl)

        if not cnf.scan_win_txt:
            cnf.root.after_cancel(self.live_task)
            self.destroy()
            focus_last_win()


class StBar(CFrame):
    def __init__(self, master):
        super().__init__(master)

        self.stbar = self.load_stbar()
        self.stbar.pack(fill=tkinter.X)

        Globals.stbar_btn = self.upd_btn
        Globals.reload_stbar = self.reload_stbar

    def load_stbar(self):
        frame = CFrame(self)

        btn = CButton(frame, text=cnf.lng.settings, padx=5)
        btn['width'] = 10
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side=tkinter.LEFT)

        CSep(frame).pack(fill=tkinter.Y, side=tkinter.LEFT, padx=15)

        self.upd_btn = CButton(frame, text=cnf.lng.update, padx=5)
        self.upd_btn['width'] = 10
        self.upd_btn.cmd(lambda e: self.update_cmd(btn))
        self.upd_btn.pack(side=tkinter.LEFT)

        return frame

    def reload_stbar(self):
        self.stbar.destroy()
        self.stbar = self.load_stbar()
        self.stbar.pack(fill=tkinter.X)

    def settings_cmd(self, btn: CButton):
        Settings()

    def update_cmd(self, btn: CButton):
        if not cnf.scan_flag:
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()
                return
        else:
            ScanerGui()
