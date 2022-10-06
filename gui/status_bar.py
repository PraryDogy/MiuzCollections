"""
Gui for status bar.
"""

import tkinter

import cfg
import sqlalchemy
from database import Config, Dbase
from utils.splashscreen import SplashScreen
from utils.utils import MyButton, MyFrame, MyLabel, SmbChecker

from .images_gui import Globals
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
        SplashScreen()
        Globals.images_reset()

    def more_less(self, **kw):
        """
        Changes thumbnails size in gui or number of thumbnails columns in gui.

        * param `delta`: int decrease or increase the previous value
        * param `min`: int min value
        * param `max`: int max value
        * param `db_name`: str value for database query (size, clmns)

        Example:
        ```
        def cmd_btn():
            more_less(delta=+1, min=1, max=10, db_mane="clmns")


        tkinter.Button(master, command=cmd_btn)

        # previous value from database = 5
        # if the button is pressed, value with name "clmns" changes to 6

        # value limit = 1, 10
        # if button was pressed and prev value 1 or 10 - nothing will happens.
        ```
        """
        size = Dbase.conn.execute(sqlalchemy.select(Config.value).where(
            Config.name==kw['db_name'])).first()[0]
        size = int(size)

        size = size + kw['delta']
        size = kw['min'] if size < kw['min'] else size
        size = kw['max'] if size > kw['max'] else size

        Dbase.conn.execute(sqlalchemy.update(Config).where(
            Config.name==kw['db_name']).values(value=str(size)))
        Globals.images_reset()


class StatusBar(MyFrame, BtnCmd):
    """
    Tkinter frame for all status bar gui items.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        SettingsSection(self)
        UpdateSection(self)
        GridSection(self)
        ClmnSection(self)
        AllWindows(self)

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


class GridSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function change thumbnails size and description.
    """
    def __init__(self, master):

        MyLabel.__init__(self, master, text='Размер фото')
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='-', padx=5)
        self.configure(width=5, height=1)
        self.cmd(lambda e: self.more_less(
            delta=-50, min=150, max=200, db_name='size'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

        MyButton.__init__(self, master, text='+', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.more_less(
            delta=+50, min=150, max=200, db_name='size'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class ClmnSection(MyLabel, MyButton, BtnCmd):
    """
    Tkinter frame with button function thumbnails columns number
    and description.
    """
    def __init__(self, master):

        MyLabel.__init__(self, master, text='Столбцы')
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='-', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.more_less(
            delta=-1, min=1, max=10, db_name='clmns'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

        MyButton.__init__(self, master, text='+', padx=5)
        self.configure(width=5, height=1, )
        self.cmd(lambda e: self.more_less(
            delta=+1, min=1, max=10, db_name='clmns'))
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