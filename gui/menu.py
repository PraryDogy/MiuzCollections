from . import (Dbase, Thumbs, conf, os, partial, re, sqlalchemy, subprocess,
               tkinter, tkmacosx)
from .widgets import *

__all__ = (
    "Menu",
    )


class MenuExtend:
    def open_finder(self, e):
        if e.widget.true_name != conf.all_colls:
            coll_path = os.path.join(conf.coll_folder, e.widget.true_name)
        else:
            coll_path = conf.coll_folder

        subprocess.check_output(["/usr/bin/open", coll_path])


class ContextMenu(tkinter.Menu, MenuExtend):
    def __init__(self, e: tkinter.Event):
        super().__init__(e.widget)

        self.add_command(
            label=conf.lang.show_finder,
            command=lambda: self.open_finder(e)
            )

        self.do_popup(e)

    def do_popup(self, e):
        try:
            self.tk_popup(e.x_root, e.y_root)
        finally:
            self.grab_release()


class Menu(tkmacosx.SFrame, MenuExtend):
    reload_menu = None
    def __init__(self, master: tkinter):
        super().__init__(
            master,
            bg = conf.bg_color,
            scrollbarwidth = 7,
            width = conf.menu_w
            )

        self.menu_buttons = []
        self.sel_btn = tkinter.Label

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()

        __class__.reload_menu = self.__reload_menu

    def re_collname(self, coll: str):
        try:
            coll = re.search("[A-Za-zА-Яа-я]+.{0,11}", coll).group(0)[:13]
            return coll
        except AttributeError:
            return coll[:13]

    def load_menu_buttons(self):
        frame = CFrame(self)

        title = CLabel(frame, text=conf.lang.menu_title)
        title.configure(font=('San Francisco Pro', 22, 'bold'))
        title.pack(pady=(0,15))
        conf.lang_menu.append(title)

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {
            coll: self.re_collname(coll)
            for coll in colls_list
            }

        menus = sorted(menus.items(), key=lambda item: item[1].casefold())
        menus = dict(menus)

        last = CButton(frame, text=conf.lang.all_colls)
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.true_name = conf.all_colls
        last.cmd(self.show_coll)
        last.pack(pady=(0, 15))
        last.bind("<Button-2>", ContextMenu)

        self.menu_buttons.append(last)
        conf.lang_menu.append(last)

        sep = CSep(frame)
        sep['bg'] = '#272727'
        sep.pack(fill=tkinter.X)

        for collection_name, menu_name in menus.items():
            btn = CButton(frame, text = menu_name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.true_name = collection_name
            btn.cmd(self.show_coll)
            btn.pack()
            btn.bind("<Button-2>", ContextMenu)

            self.menu_buttons.append(btn)

            if collection_name == conf.curr_coll:
                btn.configure(bg=conf.sel_color)
                self.sel_btn = btn

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if conf.curr_coll == conf.all_colls:
            last.configure(bg=conf.sel_color)
            self.sel_btn = last

        return frame

    def __reload_menu(self):
        self.menu_buttons.clear()
        conf.lang_menu.clear()
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()
        return
    
    def show_coll(self, e):
        conf.limit = 150

        self.sel_btn.configure(bg=conf.btn_color)
        e.widget.configure(bg=conf.sel_color)
        self.sel_btn = e.widget
        conf.curr_coll = e.widget.true_name

        from .thumbnails import Thumbnails, ThumbSearch
        ThumbSearch.reload_search()
        Thumbnails.reload_with_scroll()
