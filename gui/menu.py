from . import (Dbase, Thumbs, conf, os, re, sqlalchemy, subprocess,
               tkinter, tkmacosx)
from .widgets import *
from .gui_utils import GlobGui

__all__ = (
    "Menu",
    )


class MenuExtend:
    def reveal_coll(self, e: tkinter.Event):
        if e.widget.true_name != conf.all_colls:
            coll_path = os.path.join(conf.coll_folder, e.widget.true_name)
        else:
            coll_path = conf.coll_folder

        subprocess.check_output(["/usr/bin/open", coll_path])


class ContextMenuMenu(ContextMenu, MenuExtend):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        self.add_command(
            label=conf.lang.show_finder,
            command=lambda: self.reveal_coll(e)
            )

        self.do_popup(e)


class Menu(tkmacosx.SFrame, MenuExtend):
    def __init__(self, master: tkinter):
        self.sel_btn = tkinter.Label
        GlobGui.reload_menu = self.reload_menu

        super().__init__(
            master,
            bg = conf.bg_color,
            scrollbarwidth = 7,
            width = conf.menu_w
            )

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack()

    def fake_name(self, coll: str):
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
            self.fake_name(coll): coll
            for coll in colls_list
            }

        sort_keys = sorted(menus.keys())

        menus = {
            fake_name: menus[fake_name]
            for fake_name in sort_keys
            }

        last = CButton(frame, text=conf.lang.all_colls)
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.true_name = conf.all_colls
        last.cmd(self.show_coll)
        last.pack(pady=(0, 15))
        last.bind("<Button-2>", ContextMenuMenu)

        conf.lang_menu.append(last)

        sep = CSep(frame)
        sep['bg'] = '#272727'
        sep.pack(fill=tkinter.X)

        for fake_name, true_name in menus.items():
            btn = CButton(frame, text = fake_name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.true_name = true_name
            btn.cmd(self.show_coll)
            btn.pack()
            btn.bind("<Button-2>", ContextMenuMenu)

            if true_name == conf.curr_coll:
                btn.configure(bg=conf.sel_color)
                self.sel_btn = btn

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if conf.curr_coll == conf.all_colls:
            last.configure(bg=conf.sel_color)
            self.sel_btn = last

        return frame

    def reload_menu(self):
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

        from .thumbnails import Thumbnails, Globs

        traces = Globs.str_var.trace_vinfo()
        if traces:
            Globs.str_var.trace_vdelete(*traces[0])
        Globs.str_var.set("")

        GlobGui.reload_thumbs_scroll()
