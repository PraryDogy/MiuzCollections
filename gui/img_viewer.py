from . import (Dbase, ImageTk, Thumbs, conf, convert_to_rgb, cv2, decode_image,
               find_jpeg, find_tiff, get_coll_name, os, place_center,
               resize_image, replace_bg, sqlalchemy, tkinter)
from .widgets import *

__all__ = (
    "ImgViewer",
    )


src = str
all_src = []
img_frame = tkinter.Frame
win = tkinter.Toplevel


class ContextMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Label):
        tkinter.Menu.__init__(self, master)

        self.add_command(
            label = "Инфо",
            command = lambda: ImageInfo(src, win)
            )

        self.add_separator()

        self.add_command(
            label = "Показать в Finder",
            command = lambda: find_jpeg(src)
            )

        self.add_command(
            label = "Показать tiff",
            command = lambda: find_tiff(src)
            )

        master.bind("<Button-2>", self.do_popup)

    def do_popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class ImgViewer(CWindow):
    def __init__(self, img_src: str, src_list: list):
        global src, all_src, win
        super().__init__()

        win = self
        src = img_src
        all_src = src_list

        self.set_title()
        self["bg"] = "black"

        self.geometry(f'{conf.preview_w}x{conf.preview_h}')
        self.minsize(500, 300)

        self.configure(pady=0, padx=0)
        self.resizable(1, 1)

        self.img_frame = self.img_widget()
        self.img_frame.pack()

        conf.root.update_idletasks()

        self.img_frame['width'] = conf.preview_w
        self.img_frame['height'] = conf.preview_h

        self.thumb_place(conf.preview_w, conf.preview_h)
        self.task = conf.root.after(
            500, lambda: self.img_place(conf.preview_w, conf.preview_h))

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.bind('<Configure>', self.decect_resize)
        self.resize_task = None

        self.context = ContextMenu(self)

    def decect_resize(self, e):
        if self.resize_task:
            conf.root.after_cancel(self.resize_task)
        self.resize_task = conf.root.after(500, lambda: self.resize_win())

    def resize_win(self):
        try:
            new_w, new_h = self.winfo_width(), self.winfo_height()
        except Exception:
            print("no win")
            return

        if new_w != conf.preview_w or new_h != conf.preview_h:
            conf.preview_h = new_h
            conf.preview_w = new_w

            self.img_frame['width'] = conf.preview_w
            self.img_frame['height'] = conf.preview_h

            self.thumb_place(conf.preview_w, conf.preview_h)
            conf.root.after(
                500,
                lambda: self.img_place(conf.preview_w, conf.preview_h)
                )

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label

    def switch_img(self, ind: int):
        global src

        conf.root.after_cancel(self.task)
        try:
            src = all_src[ind]
            self.context.destroy()
            self.context = ContextMenu(self)
            self.set_title()
        except IndexError:
            src = all_src[0]
            self.set_title()

        self.thumb_place(conf.preview_w, conf.preview_h)
        self.task = conf.root.after(
            500,
            lambda: self.img_place(conf.preview_w, conf.preview_h)
            )

    def img_ind(self):
        return all_src.index(src)

    def img_set(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img_frame.configure(image=img_tk)
        self.img_frame.image_names = img_tk

    def img_click(self, e: tkinter.Event):
        if conf.preview_w == self.winfo_width():

            if e.x <= conf.preview_w//2:
                index = self.img_ind() - 1
            else:
                index = self.img_ind() + 1

            self.switch_img(index)

    def thumb_load(self):
        """
        Returns decoded non resized thumbnail from database
        """
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src==src)).first()[0]
        return decode_image(thumb)

    def thumb_place(self, width, height):
        thumb = self.thumb_load()
        resized = resize_image(thumb, width, height, False)
        rgb_thumb = convert_to_rgb(resized)
        self.img_set(rgb_thumb)

    def img_place(self, width, height):
        img_read = cv2.imread(src, cv2.IMREAD_UNCHANGED)
        
        if src.endswith(("png", "PNG")):
            img_read = replace_bg(img_read, conf.bg_color)

        resized = resize_image(img_read, width, height, False)
        img_rgb = convert_to_rgb(resized)
        try:
            self.img_set(img_rgb)
        except Exception as e:
            print(e)

    def set_title(self):
        name = src.split(os.sep)[-1]
        collection_name = get_coll_name(src)
        self.title(f"{collection_name} - {name}")

