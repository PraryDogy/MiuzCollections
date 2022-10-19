"""
Gui for status bar.
"""

import tkinter

import cfg
from utils.utils import MyButton, MyFrame, MyLabel, SmbChecker
from utils.scaner import Scaner

from .settings import Settings


class BtnCmd:
    """
    Stores functions for status bar buttons.
    """
    def open_settings(self, btn=MyButton):
        """
        Opens settings gui.
        * param `btn`: tkinter button
        """
        btn.press()
        Settings()

    def updater(self, btn=MyButton):
        """
        Run Updater from utils with Splashscreen gui from utils.
        * param `btn`: tkinter button
        """
        if not SmbChecker().check():
            return

        btn.press()
        btn.unbind('<Button-1>')

        Scaner()

        btn.cmd(lambda e: self.updater(self))


class StatusBar(MyFrame, BtnCmd):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        DynamicSection(self)
        UpdateSection(self)
        SettingsSection(self)


class SettingsSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function open gui settings and description.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='⚙', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.open_settings(self))
        self.pack(side=tkinter.LEFT, padx=(0, 0))


class UpdateSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function update collections and description.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='⟲', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.updater(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class DynamicSection(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        self.pack(side=tkinter.LEFT, padx=(0, 15))
        cfg.LIVE_LBL = self