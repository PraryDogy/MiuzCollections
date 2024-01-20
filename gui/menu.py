import os
import subprocess
import tkinter

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd
from utils import SysUtils
from typing import Literal
from .widgets import *

__all__ = ("Menu",)


class ShowColl:
    def __init__(self, e=tkinter.Event):
        from .application import app
        app.menu.show_coll(e=e)


class MenuBtns:
    btns = {}


class BtnInfo:
    def __init__(self, e: tkinter.Event) -> None:
        self.btn: CButton = e.widget.__dict__["master"]
        self.collname = MenuBtns.btns[self.btn.cget("text")]


class Context(tkinter.Menu):
    def __init__(self):
        tkinter.Menu.__init__(self)

    def sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event):
        btn_info = BtnInfo(e=e)

        try:
            btn_info.btn.configure(fg_color=cnf.blue_color)
            self.tk_popup(x=e.x_root, y=e.y_root)
        finally:
            try:
                if btn_info.collname == cnf.curr_coll:
                    btn_info.btn.configure(fg_color=cnf.lgray_color)
                else:
                    btn_info.btn.configure(fg_color=cnf.bg_color_menu)
            except tkinter.TclError:
                print("menu > Context > do_popup > finally > no btn")
            self.grab_release()


class ContextUtils(SysUtils):
    def reveal_coll_filtered_cmd(self, collname: str, filter: str):
        if collname != cnf.all_colls:
            coll_parrent = os.path.join(cnf.coll_folder, collname)
            coll_path = os.path.join(coll_parrent, filter)
        try:
            subprocess.check_output(["/usr/bin/open", coll_path])
        except (subprocess.CalledProcessError, UnboundLocalError):
            try:
                subprocess.check_output(["/usr/bin/open", coll_parrent])
            except UnboundLocalError:
                subprocess.check_output(["/usr/bin/open", cnf.coll_folder])

    def reveal_coll(self, collname: str):
        if collname != cnf.all_colls:
            coll_path = os.path.join(cnf.coll_folder, collname)
        else:
            coll_path = cnf.coll_folder

        try:
            subprocess.check_output(["/usr/bin/open", coll_path])
        except subprocess.CalledProcessError:
            subprocess.check_output(["/usr/bin/open", cnf.coll_folder])


class ContextMenuBase(Context, ContextUtils):
    def __init__(self):
        Context.__init__(self)

    def show_coll_context(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.view,
            command=lambda: ShowColl(e=e))

    def reveal_coll_context(self, collname: str):
        self.add_command(
            label=f"{cnf.lng.reveal} \"{collname}\" {cnf.lng.in_finder}",
            command=lambda:
            self.reveal_coll(collname=collname))

    def reveal_coll_filtered(self, collname: str, label: str, filter: str):
        self.add_command(
            label=f"{label}: {cnf.lng.reveal.lower()} {cnf.lng.in_finder}",
            command=lambda:
            self.reveal_coll_filtered_cmd(collname=collname, filter=filter))


class ContextMenu(ContextMenuBase):
    def __init__(self, e: tkinter.Event):
        btn_info = BtnInfo(e=e)

        ContextMenuBase.__init__(self)
        self.show_coll_context(e=e)

        self.sep()
        if btn_info.collname != cnf.all_colls:
            self.reveal_coll_context(collname=btn_info.collname)
            self.sep()

            for code_name, true_name in cnf.cust_fltr_names.items():
                self.reveal_coll_filtered(
                    collname=btn_info.collname, filter=true_name,
                    label=cnf.lng.cust_fltr_names[code_name])
        else:
            self.reveal_coll_context(collname=cnf.lng.all_colls)

        self.do_popup(e=e)


class Menu(CScroll):
    def __init__(self, master: tkinter):
        CScroll.__init__(self, master=master, fg_color=cnf.bg_color_menu,
                         corner_radius=0, width=cnf.menu_w,
                         scroll_color=cnf.sel_color_menu)

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack(anchor="w", fill="x")

    def load_colls_list(self) -> Literal["improved collection name: true collection name"]:
        menus = {}

        q = sqlalchemy.select(ThumbsMd.collection).distinct()

        for i in Dbase.conn.execute(q).fetchall():
            fakename = i[0].lstrip("0123456789").strip()
            fakename = fakename if fakename else i[0]
            menus[fakename] = i[0]
        
        sort_keys = sorted(menus.keys())

        return {fake_name: menus[fake_name] for fake_name in sort_keys}

    def load_menu_buttons(self):
        MenuBtns.btns.clear()
        menus = self.load_colls_list()

        frame = CFrame(master=self, bg=cnf.bg_color_menu)

        title = CButton(master=frame, text=cnf.lng.menu,
                        font=("San Francisco Pro", 14, "bold"),
                        fg_color=cnf.bg_color_menu,
                        text_color=cnf.tit_color_menu,
                        anchor="w")
        title.pack(pady=(15,15), padx=10, anchor="w", fill="x")

        last = CButton(master=frame, text=cnf.lng.all_colls, anchor="w",
                       fg_color=cnf.bg_color_menu,
                       text_color=cnf.fg_color_menu)
        last.pack(pady=(0, 15), fill="x", padx=10, anchor="w")
        last.cmd(self.show_coll)
        last.bind(sequence="<Button-2>", command=lambda e:
                  ContextMenu(e=e, widget=last))
        MenuBtns.btns[cnf.lng.all_colls] = cnf.all_colls

        for fakename, collname in menus.items():
            btn_text = fakename[:23]
            btn = CButton(master=frame, text=btn_text,
                          fg_color=cnf.bg_color_menu, 
                          text_color=cnf.fg_color_menu, anchor="w")
            btn.pack(fill="x", padx=10, anchor="w")
            btn.cmd(self.show_coll)
            btn.bind(sequence="<Button-2>",
                     command=lambda e: ContextMenu(e=e))
            MenuBtns.btns[btn_text] = collname

            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.sel_color_menu)
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(fg_color=cnf.sel_color_menu)

        return frame

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack(anchor="w", fill="x")

    def show_coll(self, e: tkinter.Event):
        btn_info = BtnInfo(e=e)

        cnf.curr_coll = btn_info.collname
        cnf.date_start, cnf.date_end = None, None
        cnf.search_var.set(value="")

        cnf.set_topbar_title()
        cnf.reload_scroll()
        cnf.reload_filters()
        self.reload_menu()