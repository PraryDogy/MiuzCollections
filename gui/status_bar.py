"""
Gui for status bar.
"""

import tkinter

import cfg
from utils.splashscreen import SplashScreen
from utils.utils import MyButton, MyFrame, MyLabel, SmbChecker

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

        SplashScreen()
        cfg.IMAGES_RESET()

        btn.cmd(lambda e: self.updater(self))


class StatusBar(MyFrame, BtnCmd):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        SettingsSection(self)
        UpdateSection(self)
        AllWindows(self)
        DynamicSection(self)


class SettingsSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function open gui settings and description.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Настройки')
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='⚙', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.open_settings(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class UpdateSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function update collections and description.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновить')
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='⟲', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.updater(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class AllWindows(MyLabel, MyButton):
    """
    Show all windows button
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, text="Все окна")
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='֍', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.show_all(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

    def show_all(self, btn):
        btn.press()
        for k, v in cfg.ROOT.children.items():
            if 'imagepreview' in k:
                v.lift()

class DynamicSection(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        self.pack(side=tkinter.LEFT)
        cfg.LIVE_LBL = self