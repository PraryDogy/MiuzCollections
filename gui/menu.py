from . import (Dbase, ImageTk, Thumbs, cfg, convert_to_rgb, crop_image, os,
               partial, re, sqlalchemy, subprocess, tkinter, tkmacosx)
from .widgets import CButton, CFrame, CLabel, CSep
from .scaner_gui import ScanerGui

__all__ = (
    "Menu",
    )

menu_buttons = []


def open_finder(collection_name):
    if collection_name != "last":
        coll_path = os.path.join(cfg.config['COLL_FOLDER'], collection_name)
    else:
        coll_path = cfg.config['COLL_FOLDER']

    subprocess.check_output(["/usr/bin/open", coll_path])


def show_collection(master: tkinter.Button, collection_name):
    for btn_item in menu_buttons:
        btn_item['bg'] = cfg.BUTTON

    master['bg'] = cfg.SELECTED
    cfg.config['CURR_COLL'] = collection_name

    cfg.THUMBNAILS.reload_scrollable()
    cfg.THUMBNAILS.reload_thumbnails()


class ContextMenu(tkinter.Menu):
    def __init__(self, master, collection_name):
        tkinter.Menu.__init__(self, master)
        self.btn = master
        self.collection_name = collection_name

        self.add_command(
            label = "Показать в Finder",
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
        tkmacosx.SFrame.__init__(
            self,
            master,
            bg = cfg.BG,
            scrollbarwidth = 7,
            width = 180
            )

        cfg.MENU = self

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

    def load_menu_buttons(self):
        frame = CFrame(self)

        title = CLabel(frame, text='Меню')
        title.configure(font=('San Francisco Pro', 22, 'bold'))
        title.pack(pady=(0,15))

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {
            coll: re.search("[A-Za-zА-Яа-я]+.{0,11}", coll).group(0)[:13]
            for coll in colls_list
            }

        menus = dict(
            sorted(
                menus.items(),
                key = lambda item: item[1].casefold()
                ))

        last = CButton(frame, text='Все коллекции')
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.open_coll_folder, 'last', last))
        last.pack(pady=(0, 15))
        menu_buttons.append(last)

        ContextMenu(last, "last")

        sep = CSep(frame)
        sep['bg'] = '#272727'
        sep.pack(fill=tkinter.X)
        
        scaner = CButton(frame, text = "Сканер")
        scaner.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        # scaner.pack(pady=(0, 15))
        scaner.cmd(lambda e: self.scaner_cmd())
        menu_buttons.append(scaner)

        for collection_name, menu_name in menus.items():
            btn = CButton(frame, text = menu_name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.cmd(partial(self.open_coll_folder, collection_name, btn))
            btn.pack()
            menu_buttons.append(btn)

            ContextMenu(btn, collection_name)

            if collection_name == cfg.config['CURR_COLL']:
                btn.configure(bg=cfg.SELECTED)

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if cfg.config['CURR_COLL'] == 'last':
            last.configure(bg=cfg.SELECTED)

        return frame

    def scaner_cmd(self):
        ScanerGui()

    def reload(self):
        """
        External use
        """
        menu_buttons.clear()
        self.menu_buttons.destroy()
        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()
        return
    
    def open_coll_folder(self, coll: str, btn: CButton, e):
        cfg.LIMIT = 150

        if btn['bg'] == cfg.SELECTED:
            btn['bg'] = cfg.HOVERED

            cfg.ROOT.after(
                200,
                lambda: btn.configure(bg=cfg.SELECTED)
                )

            open_finder(coll)
            return

        show_collection(btn, coll)