import tkinter

from cfg import conf
from scaner import Scaner
from utils import *

from .gui_utils import Globals
from .settings import Settings
from .widgets import *

__all__ = (
    "StBar",
    )


class ScanerGui(CWindow):
    def __init__(self):
        super().__init__()
        self.title(conf.lang.scaner_title)
        self.geometry("300x50")

        self.live_lbl = CLabel(
            self,
            text = conf.live_text,
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            )
        self.live_lbl.pack(expand=True, fill="both")

        conf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.live_task = False
        self.update_livelbl()

    def update_livelbl(self):

        if self.winfo_exists():
            self.live_lbl["text"] = conf.live_text
            self.live_task = conf.root.after(100, self.update_livelbl)

        if not conf.live_text:
            conf.root.after_cancel(self.live_task)
            self.destroy()
            focus_last()


class StBar(CFrame):
    def __init__(self, master):
        super().__init__(master)
        self.normal_mode()
        Globals.stbar_btn = self.upd_btn

    def normal_mode(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]

        btn = CButton(self, text=conf.lang.settings_title, padx=5)
        btn['width'] = 10
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side=tkinter.LEFT)
        conf.lang_st_bar.append(btn)

        CSep(self).pack(fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))

        self.upd_btn = CButton(self, text=conf.lang.upd_btn, padx=5)
        self.upd_btn['width'] = 10
        self.upd_btn.cmd(lambda e: self.update_cmd(btn))
        self.upd_btn.pack(side=tkinter.LEFT)
        conf.lang_st_bar.append(self.upd_btn)

    def settings_cmd(self, btn: CButton):
        btn.press()
        Settings()

    def update_cmd(self, btn: CButton):
        if not conf.flag:
            if smb_check():
                Scaner().auto_scan()
            else:
                SmbAlert()
                return
        else:
            ScanerGui()
