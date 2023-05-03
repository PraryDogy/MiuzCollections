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

        lbl = CLabel(self, text = "Обновляю данные:")
        lbl.pack()

        self.live_lbl = CLabel(
            self,
            text = cfg.LIVE_TEXT,
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            width = 30
            )
        self.live_lbl.pack()

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.update_livelbl()

    def update_livelbl(self):
        try:
            self.live_lbl["text"] = cfg.LIVE_TEXT
        except Exception:
            print("no livelabel")
        
        if self.winfo_exists():
            task = cfg.ROOT.after(100, self.update_livelbl)

            if not cfg.LIVE_TEXT:
                self.destroy()



class StBar(CFrame):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.ST_BAR = self
        self.normal_mode()

    def normal_mode(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]

        btn = CButton(self, text='Настройки', padx=5)
        btn['width'] = 10
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side=tkinter.LEFT)

        CSep(self).pack(fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))

        upd_btn = CButton(self, text='Обновить', padx=5)
        upd_btn['width'] = 10
        upd_btn.cmd(lambda e: self.update_cmd(btn))
        upd_btn.pack(side=tkinter.LEFT)

    def settings_cmd(self, btn: CButton):
        """
        Opens settings gui.
        * param `btn`: tkinter button
        """
        btn.press()
        Settings()

    def update_cmd(self, btn: CButton):
        """
        Run Updater from utils with Splashscreen gui from 
        * param `btn`: tkinter button
        """
        if not cfg.FLAG:
            if smb_check():
                scaner()
            else:
                SmbAlert()
                return
        else:
            ScanerGui()
