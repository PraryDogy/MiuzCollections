from . import (Dbase, ImageTk, Thumbs, cfg, convert_to_rgb, crop_image,
               datetime, decode_image, partial, sqlalchemy, tkinter, tkmacosx,
               traceback, calendar)
from .img_viewer import ImgViewer
from .widgets import CButton, CFrame, CLabel, CSep


__all__ = (
    "Gallery"
    )

months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"}


def clmns_count():
    clmns = (cfg.config['ROOT_W'] - 180) // cfg.THUMB_SIZE
    return 1 if clmns == 0 else clmns


def decode_thumbs(thumbs: tuple):
    """
    Prepares images from database for tkinter.
    * input: ((`img`, `src`, `date modified`), ...)
    * returns: ((`img`, `src`, `date modified`), ...)
    """
    result = []
    for blob, src, modified in thumbs:
        try:
            decoded = decode_image(blob)
            cropped = crop_image(decoded)
            rgb = convert_to_rgb(cropped)
            img = ImageTk.PhotoImage(rgb)
            result.append((img, src, modified))

        except Exception:
            print(traceback.format_exc())

    return result

def convert_year(thumbs: list):
    """
    Converts timestamp to year
    * input: ((`img`, `src`, `date modified`), ...)
    * returns: ((`img`, `src`, `year`), ...)
    """
    result = []
    for img, src, modified in thumbs:
        year = datetime.fromtimestamp(modified).year
        month = datetime.fromtimestamp(modified).month
        result.append((img, src, f"{months[month]} {year}"))
    return result


class Gallery(CFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.GALLERY = self
        self.clmns = 1

        cfg.ROOT.update_idletasks()

        self.load_scrollable()
        self.load_thumbnails()

        cfg.ROOT.bind('<ButtonRelease-1>', self.update_gui)

    def load_scrollable(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill=tkinter.BOTH)

        self.scrollable = tkmacosx.SFrame(
            self.scroll_parrent, bg=cfg.BG, scrollbarwidth=7)
        self.scrollable.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbnails(self):
        self.thumbnails = CFrame(self.scrollable)
        self.clmns = clmns_count()

        title = CLabel(
            self.thumbnails,
            text=cfg.config['CURR_COLL'],
            font=('Arial', 45, 'bold')
            )
        title.pack()

        if cfg.config['CURR_COLL'] == 'last':
            title.configure(text='Последние добавленные')

            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150,
                    Thumbs.src,
                    Thumbs.modified
                    ).limit(cfg.LIMIT).order_by(-Thumbs.modified)
                    ).fetchall()
        else:
            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150,
                    Thumbs.src,
                    Thumbs.modified
                    ).where(
                    Thumbs.collection == cfg.config['CURR_COLL']
                    ).limit(cfg.LIMIT).order_by(-Thumbs.modified)
                    ).fetchall()

        thumbs = decode_thumbs(res)
        thumbs = convert_year(thumbs)
        all_src = [src for img, src, year in thumbs]

        thumbs_dict = {}
        for img, src, year in thumbs:
            thumbs_dict.setdefault(year, []).append((img, src))

        for year, img_list in thumbs_dict.items():

            year_frame = CLabel(
                self.thumbnails,
                font=('Arial', 30, 'bold'),
                text=year,
                )
            year_frame.pack(pady=(35, 0))

            img_row = CFrame(self.thumbnails)
            img_row.pack(fill = tkinter.X, expand=1, anchor=tkinter.W)

            for x, (img, src) in enumerate(img_list, 1):

                thumb = CButton(img_row)
                thumb.configure(
                    width = cfg.THUMB_SIZE,
                    height = cfg.THUMB_SIZE,
                    bg=cfg.BG,
                    image = img,
                    text = src
                    )
                thumb.pack(side=tkinter.LEFT)

                thumb.image_names = img
                thumb.cmd(partial(self.open_preview, src, all_src))

                thumb.bind('<Enter>', lambda e, a=thumb: self.enter(a))
                thumb.bind('<Leave>', lambda e, a=thumb: self.leave(a))

                if x % self.clmns == 0:
                    img_row = CFrame(self.thumbnails)
                    img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        more_btn = CButton(self.thumbnails, text="Показать еще")
        more_btn.cmd(lambda e: self.show_more(e))
        more_btn.pack(pady=(15, 0))

        self.thumbnails.pack(expand=1, fill=tkinter.BOTH)

    def reload_scrollable(self):
        """
        Reloads thumbnails with scroll frame.
        """
        self.scroll_parrent.destroy()
        self.load_scrollable()

    def reload_thumbnails(self):
        """
        Reloads thumbnails without scroll frame.
        """
        self.thumbnails.destroy()
        self.load_thumbnails()

    def show_more(self, e: tkinter.Event):
        """
        Reloads thumbnails without scroll frame and with new number thumbnails.
        """
        cfg.LIMIT += 150
        self.reload_thumbnails()

    def update_gui(self, e: tkinter.Event):
        """
        Reloads thumbnails without scroll for new window size
        """
        old_w = cfg.config['ROOT_W']
        new_w = cfg.ROOT.winfo_width()

        if new_w != old_w:
            cfg.config['ROOT_W'] = new_w

            if self.clmns != clmns_count():
                w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
                cfg.config['ROOT_W'], cfg.config['ROOT_H'] = w, h
                cfg.ROOT.update_idletasks()
                self.reload_thumbnails()

    def enter(self, thumb: CButton):
        if thumb['bg'] != cfg.PRESSED:
            thumb['bg'] = cfg.SELECTED

    def leave(self, thumb: CButton):
        if thumb['bg'] != cfg.PRESSED:
            thumb['bg'] = cfg.BG

    def open_preview(self, src, all_src, e):
        ImgViewer(src, all_src)