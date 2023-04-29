from . import (Dbase, Image, ImageTk, Thumbs, cfg, close_windows,
               convert_to_rgb, cv2, datetime, decode_image, find_tiff,
               get_coll_name, os, place_center, resize_image, smb_check,
               sqlalchemy, tkinter, find_jpeg)
from .widgets import CButton, CFrame, CLabel, CWindow, InfoWidget, SmbAlert

__all__ = (
    "ImgViewer"
    )


class ImgViewer(CWindow):
    def __init__(self, img_src: str, all_src: list):
        CWindow.__init__(self)

        if not smb_check():
            close_windows()
            SmbAlert()
            return

        self.img_src = img_src
        self.all_src = all_src
        self.ln = 43

        self.title('Просмотр')

        self.win_width = cfg.config["PREVIEW_W"]
        self.win_height = cfg.config["PREVIEW_H"]
        self.geometry(f'{self.win_width}x{self.win_height}')

        self.configure(pady=0, padx=0)
        self.resizable(1, 1)

        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15))

        self.btns_frame = self.btns_widget()
        self.btns_frame.pack(pady=(0, 15))
        
        self.info_frame = self.info_widget()
        self.info_frame.pack(pady=(0, 15))

        cfg.ROOT.update_idletasks()

        wids = sum(i.winfo_reqheight() for i in self.winfo_children()[1:]) + 15*3
        self.img_height = self.win_height - wids
        self.img_frame['width'] = self.win_width
        self.img_frame['height'] = self.img_height

        self.thumb_place(self.win_width, self.img_height)
        self.task = cfg.ROOT.after(500, lambda: self.img_place(self.win_width, self.img_height))

        if cfg.COMPARE:
            st_bar = cfg.ST_BAR.winfo_children()[0]
            cfg.ROOT.after(0, lambda: st_bar.configure(text="Подготовка"))
            cfg.ROOT.after(501, self.run_compare)
            return

        place_center(self)
        self.deiconify()
        self.grab_set()

        self.bind('<ButtonRelease-1>', lambda e: self.resize_win(e))

    def resize_win(self, event: tkinter.Event):
        new_w, new_h = self.winfo_width(), self.winfo_height()

        if new_w != self.win_width or new_h != self.win_height:

            wids = sum(i.winfo_reqheight() for i in self.winfo_children()[1:]) + 15*3
            self.img_height = new_h - wids
            
            self.win_height = new_h
            self.win_width = new_w

            self.img_frame['width'] = self.win_width
            self.img_frame['height'] = self.img_height

            cfg.config['PREVIEW_W'] = self.win_width
            cfg.config['PREVIEW_H'] = self.win_height

            self.thumb_place(self.win_width, self.img_height)
            cfg.ROOT.after(500, lambda: self.img_place(self.win_width, self.img_height))

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label

    def btns_widget (self):
        frame = CFrame(self)

        open_btn = CButton(frame, text='Показать в Finder')
        open_btn.cmd(lambda e: self.find_jpeg(open_btn, e))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        tiff_btn = CButton(frame, text = "Показать tiff")
        tiff_btn.cmd(lambda e: self.find_tiff_cmd(tiff_btn, e))
        tiff_btn.pack(side = tkinter.LEFT)

        return frame
    
    def find_tiff_cmd(self, btn: CButton, e: tkinter.Event):
        btn.press()

        if not find_tiff(self.img_src):
            btn["text"] = "Не могу найти tiff"
            cfg.ROOT.after(
                1000,
                lambda: btn.configure(text = "Показать tiff")
                )

    def find_jpeg(self, btn: CButton, e: tkinter.Event):
        btn.press()
        find_jpeg(self.img_src)

    def info_widget(self):
        info1, info2 = self.create_info()
        info_widget = InfoWidget(self, self.ln, info1, info2)
        return info_widget

    def switch_img(self, ind: int):
        cfg.ROOT.after_cancel(self.task)
        try:
            self.img_src = self.all_src[ind]
            self.btns_frame.img_src = self.img_src
        except IndexError:
            self.img_src = self.all_src[0]
            self.btns_frame.img_src = self.img_src

        self.thumb_place(self.win_width, self.img_height)
        self.task = cfg.ROOT.after(500, lambda: self.img_place(self.win_width, self.img_height))

    def img_ind(self) -> int: 
        return self.all_src.index(self.img_src)

    def img_set(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img_frame.configure(image=img_tk)
        self.img_frame.image_names = img_tk

    def img_click(self, e: tkinter.Event):
        if e.x <= self.win_width//2:
            index = self.img_ind() - 1
        else:
            index = self.img_ind() + 1
        self.switch_img(index)

    def thumb_load(self):
        """
        Returns decoded non resized thumbnail from database
        """
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src==self.img_src)).first()[0]
        return decode_image(thumb)

    def thumb_place(self, width, height):
        thumb = self.thumb_load()
        resized = resize_image(thumb, width, height, False)
        rgb_thumb = convert_to_rgb(resized)
        self.img_set(rgb_thumb)

    def img_place(self, width, height):
        img_read = cv2.imread(self.img_src)
        resized = resize_image(img_read, width, height, False)
        img_rgb = convert_to_rgb(resized)
        self.img_set(img_rgb)

        info1, _, info2 = self.info_frame.winfo_children()
        info1['text'], info2['text'] = self.create_info()

    def btn_compare(self, btn: CButton):
        btn.press()
        if not cfg.COMPARE:
            cfg.ST_BAR.compare_mode()
            win = self.winfo_toplevel()
            win.withdraw()
            win.grab_release()
            cfg.COMPARE = True
            cfg.MENU.compare_mode(self.thumb_load())
            return

    def create_info(self):
        name = self.img_src.split(os.sep)[-1]
        name = self.name_cut(name, self.ln)

        path = self.img_src.replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = self.name_cut(path, self.ln)

        filesize = round(os.path.getsize(self.img_src)/(1024*1024), 2)

        filemod = datetime.fromtimestamp(os.path.getmtime(self.img_src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        w, h = Image.open(self.img_src).size

        t1 = (f'Разрешение: {w}x{h}'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        t2 = (f'Коллекция: {get_coll_name(self.img_src)}'
                f'\nИмя: {name}'
                f'\nПуть: {path}')

        return (t1, t2)

    def name_cut(self, name: str, ln: int):
        return [name[:ln]+'...' if len(name) > ln else name][0]