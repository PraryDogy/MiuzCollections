from . import (Dbase, ImageTk, Thumbs, cfg, convert_to_rgb, crop_image, os,
               partial, re, sqlalchemy, subprocess, tkinter, tkmacosx)
from .widgets import CButton, CFrame, CLabel, CSep


class Menu(tkmacosx.SFrame):
    def __init__(self, master: tkinter):
        tkmacosx.SFrame.__init__(
            self,
            master,
            bg = cfg.BGCOLOR,
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
        frame.pack(padx=15)

        self.compare_frame = CFrame(frame)

        self.compare_title = CLabel(self.compare_frame)
        self.compare_title.pack()

        self.compare_img = CLabel(self.compare_frame)
        self.compare_img.pack(pady=(0, 15))

        menu_frame = CFrame(frame)
        menu_frame.pack(side=tkinter.BOTTOM)

        return frame

    def load_menu_buttons(self):
        frame = CFrame(self)

        title = CLabel(
            frame, text='Коллекции', font=('Arial', 22, 'bold'))
        title.pack(pady=(0,15))

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {
            coll: re.sub(r'[^a-zA-Zа-яА-Я ]+', '', coll).lstrip()[:13]
            for coll in colls_list
            }
        menus = dict(
            sorted(
                menus.items(),
                key=lambda item: item[1].casefold()
                ))

        btns = []

        last = CButton(frame, text='Последние')
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.open_coll_folder, 'last', last, btns))
        last.pack(fill=tkinter.X, pady=(0, 15))
        btns.append(last)

        for full_name, name in menus.items():
            btn = CButton(frame, text = name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.cmd(partial(self.open_coll_folder, full_name, btn, btns))
            btn.pack(fill=tkinter.X)
            btns.append(btn)

            if full_name == cfg.config['CURR_COLL']:
                btn.configure(bg=cfg.BGPRESSED)

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if cfg.config['CURR_COLL'] == 'last':
            last.configure(bg=cfg.BGPRESSED)

        return frame

    def compare_mode(self, thumbnail):
        """
        External use
        """
        cropped = crop_image(thumbnail)
        rgb_thumb = convert_to_rgb(cropped)
        img_tk = ImageTk.PhotoImage(rgb_thumb)

        self.compare_img['image'] = img_tk
        self.compare_img.image_names = img_tk

        self.compare_title['text'] = 'В списке сравнения:'

        self.compare_frame.pack(side=tkinter.TOP)

    def normal_mode(self):
        """
        External use
        """
        self.compare_img['image'] = ''
        self.compare_title['text'] = ''
        self.compare_frame.pack_forget()

    def reload(self):
        """
        External use
        """
        self.menu_buttons.destroy()
        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()
        return
    
    def open_coll_folder(self, coll: str, btn: CButton, btns: list, e):
        if coll != "last":
            coll_path = os.path.join(
                cfg.config['COLL_FOLDER'],
                coll
                )
        else:
            coll_path = cfg.config['COLL_FOLDER']

        if btn['bg'] == cfg.BGPRESSED:
            btn['bg'] = cfg.BGSELECTED

            cfg.ROOT.after(
                200,
                lambda: btn.configure(bg=cfg.BGPRESSED)
                )

            subprocess.check_output(["/usr/bin/open", coll_path])
            return

        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON

        btn['bg'] = cfg.BGPRESSED
        cfg.config['CURR_COLL'] = coll

        cfg.GALLERY.reload()