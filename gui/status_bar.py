"""
Gui for status bar.
"""

import tkinter

import cfg
from scaner import scaner
from utils import smb_check

from .widgets import CButton, CFrame, CLabel, CSep, SmbAlert
from .settings import Settings


class StatusBar(CFrame):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.STATUSBAR_NORMAL = self.pack_widgets
        cfg.STATUSBAR_COMPARE = self.pack_compare
        self.pack_widgets()

    def pack_widgets(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]
        FakeLabel(self).pack(side=tkinter.LEFT, padx=(0, 15))
        SettingsSection(self).pack(side=tkinter.LEFT)
        CSep(self).pack(
            fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))
        UpdateSection(self).pack(side=tkinter.LEFT, padx=(0, 15))
        DynamicSection(self).pack(side=tkinter.LEFT, padx=(0, 15))

    def pack_compare(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]
        CompareTitle(self)


class FakeLabel(CLabel):
    def __init__(self, master):
        CLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        cfg.LIVE_LBL = self


class SettingsSection(CLabel, CButton):
    """
    Tkinter frame with button function open gui settings and description.
    """
    def __init__(self, master):
        CButton.__init__(self, master, text='Настройки', padx=5)
        self.configure(width=8)
        self.cmd(lambda e: self.open_settings(self))

    def open_settings(self, btn: CButton):
        """
        Opens settings gui.
        * param `btn`: tkinter button
        """
        btn.press()
        Settings()


class UpdateSection(CLabel, CButton):
    """
    Tkinter frame with button function update collections and description.
    """
    def __init__(self, master):
        CButton.__init__(self, master, text='Обновить', padx=5)
        self.configure(width=8)
        self.cmd(lambda e: self.updater(self))

    def updater(self, btn: CButton):
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


class DynamicSection(CLabel):
    def __init__(self, master):
        CLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        cfg.LIVE_LBL = self


class CompareTitle(CFrame):
    def __init__(self, master: tkinter.Frame):
        subtitle = CLabel(
            master, 
            fg=cfg.BGFONT,
            text='Выберите фото для сравнения или нажмите Esc для отмены')
        subtitle.pack(side=tkinter.LEFT)

        cancel = CButton(master, text='Отмена')
        cancel.configure(width=8)
        cancel.cmd(lambda e: self.cancel())
        cancel.pack(side=tkinter.LEFT, padx=(15, 0))
        cfg.ROOT.bind('<Escape>', lambda e: self.cancel())

    def cancel(self):
        cfg.ROOT.unbind('<Escape>')
        cfg.STATUSBAR_NORMAL()
        for i in cfg.THUMBS:
            if i['bg'] == cfg.BGPRESSED:
                i['bg'] = cfg.BGCOLOR
                break
        cfg.COMPARE = False
        windows = tuple(v for k, v in cfg.ROOT.children.items() if "preview" in k)
        [w.destroy() for w in windows]