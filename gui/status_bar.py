"""
Gui for status bar.
"""

import tkinter

import cfg
from scaner import scaner
from utils import MyButton, MyFrame, MyLabel, MySep, smb_check

from .settings import Settings
from .smb_checker import SmbChecker


class StatusBar(MyFrame):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        cfg.STATUSBAR_NORMAL = self.pack_widgets
        cfg.STATUSBAR_COMPARE = self.pack_compare
        self.pack_widgets()

    def pack_widgets(self):
        widgets = [v for k, v in self.children.items()]
        [i.destroy() for i in widgets]
        FakeLabel(self).pack(side=tkinter.LEFT, padx=(0, 15))
        SettingsSection(self).pack(side=tkinter.LEFT)
        MySep(self, orient='vertical').pack(
            fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))
        UpdateSection(self).pack(side=tkinter.LEFT, padx=(0, 15))
        DynamicSection(self).pack(side=tkinter.LEFT, padx=(0, 15))

    def pack_compare(self):
        widgets = [v for k, v in self.children.items()]
        [i.destroy() for i in widgets]
        CompareTitle(self)


class FakeLabel(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        cfg.LIVE_LBL = self


class SettingsSection(MyLabel, MyButton):
    """
    Tkinter frame with button function open gui settings and description.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='⚙', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.open_settings(self))

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

    def updater(self, btn: MyButton):
        """
        Run Updater from utils with Splashscreen gui from 
        * param `btn`: tkinter button
        """
        if not cfg.FLAG:
            if not smb_check():
                SmbChecker()
                return
            btn.press()
            btn.unbind('<ButtonRelease-1>')
            scaner()
            btn.cmd(lambda e: self.updater(self))

class DynamicSection(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновление 00%')
        self['fg'] = cfg.BGCOLOR
        cfg.LIVE_LBL = self


class CompareTitle(MyFrame):
    def __init__(self, master: tkinter.Frame):
        subtitle = MyLabel(
            master, 
            fg=cfg.BGFONT,
            text='Выберите фото для сравнения')
        subtitle.pack(side=tkinter.LEFT)

        cancel = MyButton(master, text='Отмена')
        cancel.configure(height=1, width=10)
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
        windows = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
        [w.destroy() for w in windows]