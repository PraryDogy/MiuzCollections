import re
import tkinter

import sqlalchemy
import tkmacosx

from cfg import cnf
from database import Dbase, Thumbs

from .globals import Globals
from .widgets import *

__all__ = (
    "Menu",
    )


class ContextMenu(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.show_coll(e)
        self.reveal_coll(e)
        self.sep()

        self.apply_filter(cnf.lng.product, e)
        self.apply_filter(cnf.lng.models, e)
        self.apply_filter(cnf.lng.catalog, e)
        self.apply_filter(cnf.lng.show_all, e)

        self.do_popup(e)


class Menu(tkmacosx.SFrame):
    def __init__(self, master: tkinter):
        self.sel_btn: tkinter.Label = None
        Globals.reload_menu = self.reload_menu

        super().__init__(
            master,
            bg = cnf.bg_color,
            scrollbarwidth = 7,
            width = cnf.menu_w
            )

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()
        self.bind("<Enter>", lambda e: self.focus_force)
        Globals.show_coll = self.show_coll

    def fake_name(self, coll: str):
        try:
            coll = re.search("[A-Za-zА-Яа-я]+.{0,11}", coll).group(0)[:13]
            return coll
        except AttributeError:
            return coll[:13]

    def load_menu_buttons(self):
        frame = CFrame(self)

        title = CLabel(frame, text=cnf.lng.menu)
        title.configure(font=('San Francisco Pro', 22, 'bold'))
        title.pack(pady=(0,15))

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {
            self.fake_name(coll): coll
            for coll in colls_list
            }

        sort_keys = sorted(menus.keys())

        menus = {
            fake_name: menus[fake_name]
            for fake_name in sort_keys
            }

        last = CButton(frame, text=cnf.lng.all_colls)
        last.configure(width=13, pady=5, anchor="w", padx=10)
        last.coll_name = cnf.all_colls
        last.cmd(self.show_coll)
        last.pack(pady=(0, 15))
        last.bind("<Button-2>", ContextMenu)

        sep = CSep(frame)
        sep['bg'] = '#272727'
        sep.pack(fill="x")

        for fake_name, coll_name in menus.items():
            btn = CButton(frame, text=fake_name)
            btn.configure(width=13, pady=5, anchor="w", padx=10)
            btn.coll_name = coll_name
            btn.cmd(self.show_coll)
            btn.pack()
            btn.bind("<Button-2>", ContextMenu)

            if coll_name == cnf.curr_coll:
                btn.configure(bg=cnf.lgray_color)
                self.sel_btn = btn

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill="x")
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(bg=cnf.lgray_color)
            self.sel_btn = last

        return frame

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()
        return
    
    def show_coll(self, e):
        cnf.limit = 150

        self.sel_btn.configure(bg=cnf.btn_color)
        e.widget.configure(bg=cnf.lgray_color)
        self.sel_btn = e.widget
        cnf.curr_coll = e.widget.coll_name

        Globals.start, Globals.end = None, None
        Globals.search_var.set("")
        Globals.reload_scroll()
