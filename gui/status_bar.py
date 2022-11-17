"""
Gui for status bar.
"""

import tkinter
from tkinter.ttk import Separator

import cfg
from scaner import scaner
from utils import MyButton, MyFrame, MyLabel, smb_check

from .settings import Settings
from .smb_checker import SmbChecker


class StatusBar(MyFrame):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        FakeLabel(self)
        SettingsSection(self)
        Separator(self, orient='vertical').pack(
            fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))
        UpdateSection(self)
        DynamicSection(self)


class FakeLabel(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        self.pack(side=tkinter.LEFT, padx=(0, 15))
        cfg.LIVE_LBL = self

class SettingsSection(MyLabel, MyButton):
    """
    Tkinter frame with button function open gui settings and description.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='⚙', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.open_settings(self))
        self.pack(side=tkinter.LEFT, padx=(0, 0))

    def open_settings(self, btn: MyButton):
        """
        Opens settings gui.
        * param `btn`: tkinter button
        """
        btn.press()
        Settings()


class UpdateSection(MyLabel, MyButton):
    """
    Tkinter frame with button function update collections and description.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='⟲', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.updater(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

    def updater(self, btn: MyButton):
        """
        Run Updater from utils with Splashscreen gui from 
        * param `btn`: tkinter button
        """
        if not smb_check():
            SmbChecker()
            return

        btn.press()
        btn.unbind('<Button-1>')
        scaner()
        btn.cmd(lambda e: self.updater(self))


class DynamicSection(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        self.pack(side=tkinter.LEFT, padx=(0, 15))
        cfg.LIVE_LBL = self
