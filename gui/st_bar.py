from . import cfg, tkinter, smb_check, scaner

from .widgets import CButton, CFrame, CLabel, CSep, SmbAlert
from .settings import Settings


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

        btn = CButton(self, text='Обновить', padx=5)
        btn['width'] = 10
        btn.cmd(lambda e: self.update_cmd(btn))
        btn.pack(side=tkinter.LEFT)

    def compare_mode(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]

        subtitle = CLabel(
            self,
            fg = cfg.BGFONT,
            text = 'Выберите фото для сравнения или нажмите Esc для отмены'
            )
        subtitle.pack(side=tkinter.LEFT)

        cancel = CButton(self, text='Отмена')
        cancel['width'] = 8
        cancel.cmd(lambda e: self.cancel_cmd())
        cancel.pack(side=tkinter.LEFT, padx=(15, 0))
        cfg.ROOT.bind('<Escape>', lambda e: self.cancel_cmd())

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
            if not smb_check():
                SmbAlert()
                return
            btn.press()
            scaner()

    def cancel_cmd(self):
        cfg.ROOT.unbind('<Escape>')
        self.normal_mode()
        cfg.COMPARE = False
        cfg.MENU.remove_thumb()
        windows = (v for k, v in cfg.ROOT.children.items() if "preview" in k)
        [w.destroy() for w in windows]