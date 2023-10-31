import re
import tkinter

import sqlalchemy
import tkmacosx

from cfg import cnf
from database import Dbase, Thumbs

from .widgets import *

__all__ = (
    "Menu",
    )


class ContextMenu(Context):
    def __init__(self, e: tkinter.Event, collname):
        super().__init__()
        self.show_coll(e, collname)
        self.reveal_coll(collname)
        self.sep()

        self.apply_filter(e, cnf.lng.product, collname)
        self.apply_filter(e, cnf.lng.models, collname)
        self.apply_filter(e, cnf.lng.catalog, collname)
        self.apply_filter(e, cnf.lng.show_all, collname)

        self.do_popup_menu(e, collname)


class Menu(tkmacosx.SFrame):
    def __init__(self, master: tkinter):
        self.sel_btn: tkinter.Label = None

        super().__init__(
            master,
            bg=cnf.menugray,
            scrollbarwidth = 7,
            width = cnf.menu_w
            )

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack(fill="x")
        self.bind("<Enter>", lambda e: self.focus_force)

    def fake_name(self, coll: str):
        try:
            coll = re.search("[A-Za-zА-Яа-я]+.{0,11}", coll).group(0)[:13]
            return coll
        except AttributeError:
            return coll[:13]

    def load_menu_buttons(self):
        bl_frame = CFrame(self, bg="black")

        bd_frame = CFrame(bl_frame, bg=cnf.grayfont)
        bd_frame.pack(fill="both", expand=1, padx=1, pady=1)

        frame = CFrame(bd_frame, bg=cnf.menugray)
        frame.pack(fill="both", expand=1, padx=1, pady=1)

        title = CLabel(
            frame, text=cnf.lng.menu, font=("San Francisco Pro", 14, "bold"),
            bg=cnf.menugray, fg=cnf.grayfont, anchor="w", padx=5
            )
        title.pack(pady=(15,15), padx=10, fill="x")

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

        last = CButton(
            frame, text=cnf.lng.all_colls, pady=5,
            anchor="w", padx=5, bg=cnf.menugray
            )
        last.cmd(lambda e: self.show_coll(e, cnf.all_colls))
        last.bind("<Button-2>", lambda e: ContextMenu(e, cnf.all_colls))
        last.pack(pady=(0, 15), fill="x", padx=10)

        for fakename, collname in menus.items():
            btn = CButton(
                frame, text=fakename, pady=5, anchor="w", padx=5,
                bg=cnf.menugray
                )
            btn.cmd(lambda e, collname=collname: self.show_coll(e, collname))
            btn.pack(fill="x", padx=10)
            btn.bind("<Button-2>", (
                lambda e, collname=collname: ContextMenu(e, collname)
                ))

            if collname == cnf.curr_coll:
                btn.configure(bg=cnf.selectgray)
                self.sel_btn = btn
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(bg=cnf.selectgray)
            self.sel_btn = last

        return bl_frame

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()
        return
    
    def show_coll(self, e: tkinter.Event, collname):
        cnf.limit = 150

        self.sel_btn.configure(bg=cnf.menugray)
        e.widget.configure(bg=cnf.selectgray)
        self.sel_btn = e.widget
        cnf.curr_coll = collname

        cnf.start, cnf.end = None, None
        cnf.search_var.set("")
        cnf.reload_scroll()