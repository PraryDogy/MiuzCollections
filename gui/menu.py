import re
import tkinter

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd

from .widgets import *

__all__ = (
    "Menu",
    )


class ContextMenu(Context):
    def __init__(self, e: tkinter.Event, btn, collname):
        super().__init__()
        self.show_coll(e, btn, collname)
        self.reveal_coll(collname)
        self.sep()

        self.apply_filter(
            e, label=cnf.lng.product, filter="prod", collname=collname)
        self.apply_filter(
            e, label=cnf.lng.models, filter="mod", collname=collname)
        self.apply_filter(
            e, label=cnf.lng.catalog, filter="cat", collname=collname)
        self.apply_filter(
            e, label=cnf.lng.show_all, filter="all", collname=collname)

        self.do_popup_menu(e, btn, collname)


class Menu(CScroll):
    def __init__(self, master: tkinter):
        self.sel_btn: tkinter.Label = None

        super().__init__(
            master, fg_color=cnf.bg_color_menu, corner_radius=3,
            width=cnf.menu_w
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
        frame = CFrame(self, bg=cnf.bg_color_menu)
        frame.pack(fill="both", expand=1)

        title = CLabel(
            frame, text=cnf.lng.menu, font=("San Francisco Pro", 14, "bold"),
            bg=cnf.bg_color_menu, fg=cnf.tit_color_menu, anchor="w", padx=5
            )
        title.pack(pady=(15,15), padx=10, fill="x")

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(ThumbsMd.collection)
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
            frame, text=cnf.lng.all_colls, anchor="w",
            fg_color=cnf.bg_color_menu, text_color=cnf.fg_color_menu
            )
        last.cmd(
            lambda e: self.show_coll(e, last, cnf.all_colls)
            )
        last.bind("<Button-2>", lambda e: ContextMenu(e, last, cnf.all_colls))
        last.pack(pady=(0, 15), fill="x", padx=10)

        for fakename, collname in menus.items():
            btn = CButton(
                frame, text=fakename, anchor="w",
                fg_color=cnf.bg_color_menu, text_color=cnf.fg_color_menu
                )
            btn.cmd(
                lambda e,
                btn=btn, collname=collname: self.show_coll(e, btn, collname)
                )
            btn.pack(fill="x", padx=10)
            btn.bind("<Button-2>", (
                lambda e,
                btn=btn, collname=collname: ContextMenu(e,btn, collname)
                ))

            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.sel_color_menu)
                self.sel_btn = btn
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(fg_color=cnf.sel_color_menu)
            self.sel_btn = last

        return frame

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()
        return
    
    def show_coll(self, e: tkinter.Event, btn: tkinter.Label, collname):
        cnf.limit = 150

        self.sel_btn.configure(fg_color=cnf.bg_color_menu)
        btn.configure(fg_color=cnf.sel_color_menu)
        self.sel_btn = btn
        cnf.curr_coll = collname

        cnf.start, cnf.end = None, None
        cnf.search_var.set("")
        cnf.reload_scroll()