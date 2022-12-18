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
        cfg.ST_BAR = self
        self.normal()

    def normal(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]

        self.fake_widget(self).pack(side=tkinter.LEFT, padx=(0, 15))
        self.settings_widget(self).pack(side=tkinter.LEFT)
        CSep(self).pack(fill=tkinter.Y, side=tkinter.LEFT, padx=(15, 15))
        self.update_widget(self).pack(side=tkinter.LEFT, padx=(0, 15))
        live_wid = self.live_widget(self)
        live_wid.pack(side=tkinter.LEFT, padx=(0, 15))
        cfg.LIVE_LBL = live_wid

    def compare(self):
        widgets = tuple(v for k, v in self.children.items())
        [i.destroy() for i in widgets]
        self.compare_wid = self.compare_widget(self)
        self.compare_wid.pack()

    def wait(self):
        widgets = self.compare_wid.winfo_children()
        widgets[0]['text'] = 'Подготовка'

    def fake_widget(self, master: tkinter):
        label = CLabel(master, text='Обновление 00%')
        label['fg'] = cfg.BGCOLOR
        return label

    def settings_widget(self, master: tkinter):
        btn = CButton(master, text='Настройки', padx=5)
        btn['width'] = 8
        btn.cmd(lambda e: self.open_settings(btn))
        return btn

    def open_settings(self, btn: CButton):
        """
        Opens settings gui.
        * param `btn`: tkinter button
        """
        btn.press()
        Settings()

    def update_widget(self, master: tkinter):
        btn = CButton(master, text='Обновить', padx=5)
        btn['width'] = 8
        btn.cmd(lambda e: self.updater(btn))
        return btn

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

    def live_widget(self, master):
        lbl = CLabel(master, text='Обновление 00%')
        lbl['fg'] = cfg.BGCOLOR
        return lbl

    def compare_widget(self, master: tkinter):
        frame = CFrame(master)

        subtitle = CLabel(frame,fg=cfg.BGFONT,
            text='Выберите фото для сравнения или нажмите Esc для отмены')
        subtitle.pack(side=tkinter.LEFT)

        cancel = CButton(frame, text='Отмена')
        cancel['width'] = 8
        cancel.cmd(lambda e: self.cancel())
        cancel.pack(side=tkinter.LEFT, padx=(15, 0))
        cfg.ROOT.bind('<Escape>', lambda e: self.cancel())

        return frame

    def cancel(self):
        cfg.ROOT.unbind('<Escape>')
        self.normal()
        for i in cfg.GALLERY.thumbs_list:
            if i['bg'] == cfg.BGPRESSED:
                i['bg'] = cfg.BGCOLOR
                break
        cfg.COMPARE = False
        windows = tuple(v for k, v in cfg.ROOT.children.items() if "preview" in k)
        [w.destroy() for w in windows]