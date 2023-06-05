from . import (Dbase, Thumbs, conf, os, partial, re, sqlalchemy, subprocess,
               tkinter, tkmacosx)
from .widgets import *

__all__ = (
    "Menu",
    )

menu_buttons = []


def open_finder(collection_name):
    if collection_name != conf.all_colls:
        coll_path = os.path.join(conf.coll_folder, collection_name)
    else:
        coll_path = conf.coll_folder

    subprocess.check_output(["/usr/bin/open", coll_path])


def show_collection(master: tkinter.Button, collection_name):
    for btn_item in menu_buttons:
        btn_item['bg'] = conf.btn_color

    master['bg'] = conf.sel_color
    conf.curr_coll = collection_name

    from . import app
    app.thumbnails.reload_with_scroll()


class ContextMenu(tkinter.Menu):
    def __init__(self, master, collection_name):
        super().__init__(master)
        self.btn = master
        self.collection_name = collection_name

        self.add_command(
            label = conf.lang.show_finder,
            command = lambda: open_finder(collection_name)
            )

        master.bind("<Button-2>", self.do_popup)

    def do_popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class Menu(tkmacosx.SFrame):
    def __init__(self, master: tkinter):
        super().__init__(
            master,
            bg = conf.bg_color,
            scrollbarwidth = 7,
            width = conf.menu_w
            )

        self.menu_parrent = self.load_menu_parent()
        self.menu_parrent.pack()

        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()

    def load_menu_parent(self):
        frame = CFrame(self)
        frame.pack()

        menu_frame = CFrame(frame)
        menu_frame.pack(side=tkinter.BOTTOM)

        return frame

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

        menus = dict(
            sorted(
                menus.items(),
                key = lambda item: item[1].casefold()
                ))

        last = CButton(frame, text=conf.lang.all_colls)
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.open_coll_folder, conf.all_colls, last))
        last.pack(pady=(0, 15))
        menu_buttons.append(last)
        conf.lang_menu.append(last)

        ContextMenu(last, conf.all_colls)

        sep = CSep(frame)
        sep['bg'] = '#272727'
        sep.pack(fill=tkinter.X)

        for collection_name, menu_name in menus.items():
            btn = CButton(frame, text = menu_name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.cmd(partial(self.open_coll_folder, collection_name, btn))
            btn.pack()
            menu_buttons.append(btn)

            ContextMenu(btn, collection_name)

            if collection_name == conf.curr_coll:
                btn.configure(bg=conf.sel_color)

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if conf.curr_coll == conf.all_colls:
            last.configure(bg=conf.sel_color)

        return frame

    def reload(self):
        menu_buttons.clear()
        conf.lang_menu.clear()
        self.menu_buttons.destroy()
        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()
        return
    
    def open_coll_folder(self, coll: str, btn: CButton, e):
        conf.limit = 150
        show_collection(btn, coll)