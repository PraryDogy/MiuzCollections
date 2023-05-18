from . import cfg, place_center, scaner, smb_check, tkinter
from .settings import Settings
from .widgets import *

__all__ = (
    "StBar",
    )


class ScanerGui(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title("Обновление")
        self.geometry("300x50")

        self.live_lbl = CLabel(
            self,
            text = cfg.LIVE_TEXT,
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            )
        self.live_lbl.pack(expand=True, fill="both")

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.update_livelbl()

    def update_livelbl(self):
        if self.winfo_exists():
            self.live_lbl["text"] = cfg.LIVE_TEXT

        if not cfg.LIVE_TEXT:
            self.destroy()

        cfg.ROOT.after(100, self.update_livelbl)



class StBar(CFrame):
    def __init__(self, master):
        CFrame.__init__(self, master)
        self.normal_mode()

    def normal_mode(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]

        btn = CButton(self, text='Настройки', padx=5)
        btn['width'] = 10
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side=tkinter.LEFT)

        CSep(self).pack(fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))

        self.upd_btn = CButton(self, text='Обновить', padx=5)
        self.upd_btn['width'] = 10
        self.upd_btn.cmd(lambda e: self.update_cmd(btn))
        self.upd_btn.pack(side=tkinter.LEFT)

    def settings_cmd(self, btn: CButton):
        btn.press()
        Settings()

    def update_cmd(self, btn: CButton):
        if not cfg.FLAG:
            if smb_check():
                scaner()
            else:
                SmbAlert()
                return
        else:
            ScanerGui()

    def upd_btn_change(self):
        return self.upd_btn