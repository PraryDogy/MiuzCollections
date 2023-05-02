from . import (Dbase, Image, ImageTk, Thumbs, cfg,
               convert_to_rgb, cv2, datetime, decode_image, find_jpeg,
               find_tiff, get_coll_name, os, place_center, resize_image,
               smb_check, sqlalchemy, tkinter, textwrap)
from .widgets import CButton, CFrame, CLabel, CWindow, SmbAlert

__all__ = (
    "ImgViewer"
    )


src = str
all_src = []
img_frame = tkinter.Frame
win = tkinter.Toplevel


class ImageInfo(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title("Инфо")
        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        coll = f'Коллекция: {get_coll_name(src)}'
        name = f"Имя файла: {name}"
        modified = f'Дата изменения: {filemod}'
        res = f'Разрешение: {w}x{h}'
        filesize = f"Размер: {filesize}мб"
        path = f"Местонахождение: {src}"

        ln = 50

        rows = [
            i if len(i) <= ln else i[:ln] + "..."
            for i in (coll, name, modified, res, filesize, path)
            ]
        
        text = "\n".join(rows)

        lbl = CLabel(
            self,
            text = text,
            justify = tkinter.LEFT,
            anchor = tkinter.W,
            width = 40,
            )
        lbl.pack()

        self.protocol("WM_DELETE_WINDOW", lambda: self.close_win())
        self.bind('<Command-w>', lambda e: self.close_win())
        self.bind('<Escape>', lambda e: self.close_win())

        cfg.ROOT.update_idletasks()

        x, y = win.winfo_x(), win.winfo_y()
        xx = x + win.winfo_width()//2 - self.winfo_width()//2
        yy = y + win.winfo_height()//2 - self.winfo_height()//2

        self.geometry(f'+{xx}+{yy}')

        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_win(self):
        self.destroy()
        win.focus_force()
        win.grab_set_global()


class ContextMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Label):
        tkinter.Menu.__init__(self, master)

        self.add_command(
            label = "Инфо",
            command = lambda: ImageInfo()
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
        CWindow.__init__(self)

        if not smb_check():
            self.destroy()
            cfg.ROOT.focus_force()
            SmbAlert()
            return

        win = self
        src = img_src
        all_src = src_list

        self.set_title()
        self["bg"] = "black"

        self.win_width = cfg.config["PREVIEW_W"]
        self.win_height = cfg.config["PREVIEW_H"]

        self.geometry(f'{self.win_width}x{self.win_height}')

        self.configure(pady=0, padx=0)
        self.resizable(1, 1)

        self.img_frame = self.img_widget()
        self.img_frame.pack()

        cfg.ROOT.update_idletasks()

        self.img_frame['width'] = self.win_width
        self.img_frame['height'] = self.win_height

        self.thumb_place(self.win_width, self.win_height)
        self.task = cfg.ROOT.after(
            500, lambda: self.img_place(self.win_width, self.win_height))

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.bind('<Configure>', self.decect_resize)
        self.resize_task = None

        self.context = ContextMenu(self)

    def decect_resize(self, e):
        if self.resize_task:
            cfg.ROOT.after_cancel(self.resize_task)
        self.resize_task = cfg.ROOT.after(500, lambda: self.resize_win())

    def resize_win(self):
        try:
            new_w, new_h = self.winfo_width(), self.winfo_height()
        except Exception:
            print("no win")
            return

        if new_w != self.win_width or new_h != self.win_height:
            self.win_height = new_h
            self.win_width = new_w

            self.img_frame['width'] = self.win_width
            self.img_frame['height'] = self.win_height

            cfg.config['PREVIEW_W'] = self.win_width
            cfg.config['PREVIEW_H'] = self.win_height

            self.thumb_place(self.win_width, self.win_height)
            cfg.ROOT.after(
                500,
                lambda: self.img_place(self.win_width, self.win_height)
                )

            self.focus_force()

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label
    
    def find_tiff_cmd(self, btn: CButton, e: tkinter.Event):
        btn.press()
        find_tiff(src)

    def find_jpeg(self, btn: CButton, e: tkinter.Event):
        btn.press()
        find_jpeg(src)

    def switch_img(self, ind: int):
        global src

        cfg.ROOT.after_cancel(self.task)
        try:
            src = all_src[ind]
            self.context.destroy()
            self.context = ContextMenu(self)
            self.set_title()
        except IndexError:
            src = all_src[0]
            self.set_title()

        self.thumb_place(self.win_width, self.win_height)
        self.task = cfg.ROOT.after(
            500,
            lambda: self.img_place(self.win_width, self.win_height)
            )

    def img_ind(self) -> int:
        return all_src.index(src)

    def img_set(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img_frame.configure(image=img_tk)
        self.img_frame.image_names = img_tk

    def img_click(self, e: tkinter.Event):
        if self.win_width == self.winfo_width():

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
            Thumbs.src==src)).first()[0]
        return decode_image(thumb)

    def thumb_place(self, width, height):
        thumb = self.thumb_load()
        resized = resize_image(thumb, width, height, False)
        rgb_thumb = convert_to_rgb(resized)
        self.img_set(rgb_thumb)

    def img_place(self, width, height):
        img_read = cv2.imread(src)
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

