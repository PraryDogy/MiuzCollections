from . import (Dbase, ImageTk, Thumbs, cfg, convert_to_rgb, crop_image,
               datetime, decode_image, partial, sqlalchemy, tkinter, tkmacosx,
               traceback)
from .img_viewer import ImgViewer
from .widgets import CButton, CFrame, CLabel


def clmns_count():
    return (cfg.config['ROOT_W'] - 180)//cfg.THUMB_SIZE


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
        result.append((img, src, year))
    return result


class Gallery(CFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.GALLERY = self

        cfg.ROOT.update_idletasks()

        self.thumbs_widget = self.load_thumbs_widget(self)
        self.thumbs_widget.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        self.clmns = 0

        cfg.ROOT.bind('<ButtonRelease-1>', self.update_gui)

    def load_thumbs_widget(self, master: tkinter):
        frame = CFrame(master)
        scrollable = tkmacosx.SFrame(frame, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrollable.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        self.clmns = clmns_count()

        title = CLabel(
            scrollable,
            text=cfg.config['CURR_COLL'],
            font=('Arial', 45, 'bold')
            )
        title.pack(pady=(0, 15))

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
                    ).order_by(
                    -Thumbs.modified)
                    ).fetchall()

        thumbs = decode_thumbs(res)
        thumbs = convert_year(thumbs)
        all_src = [src for img, src, year in thumbs]

        thumbs_dict = {}
        for img, src, year in thumbs:
            thumbs_dict.setdefault(year, []).append((img, src))

        for year, img_list in thumbs_dict.items():

            year_frame = CLabel(
                scrollable,
                font=('Arial', 35, 'bold'),
                text=year,
                )
            year_frame.pack(pady=15)

            img_row = CFrame(scrollable)
            img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

            for x, (img, src) in enumerate(img_list, 1):

                thumb = CButton(img_row)
                thumb.configure(
                    width = cfg.THUMB_SIZE,
                    height = cfg.THUMB_SIZE,
                    bg=cfg.BGCOLOR,
                    image = img,
                    text = src
                    )
                thumb.pack(side=tkinter.LEFT)

                thumb.image_names = img
                thumb.cmd(partial(self.open_preview, src, all_src))

                thumb.bind('<Enter>', lambda e, a=thumb: self.enter(a))
                thumb.bind('<Leave>', lambda e, a=thumb: self.leave(a))

                if x % self.clmns == 0:
                    img_row = CFrame(scrollable)
                    img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        return frame

    def update_gui(self, e: tkinter.Event):
        old_w = cfg.config['ROOT_W']
        new_w = cfg.ROOT.winfo_width()

        if new_w != old_w:
            cfg.config['ROOT_W'] = new_w

            if self.clmns != clmns_count():
                self.reload()

    def reload(self):
        """
        External use
        Destroys `ImagesThumbs` object and run it again.
        """
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        cfg.config['ROOT_W'], cfg.config['ROOT_H'] = w, h

        self.thumbs_widget.destroy()

        self.thumbs_widget = self.load_thumbs_widget(self)
        self.thumbs_widget.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

    def enter(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGSELECTED

    def leave(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGCOLOR

    def open_preview(self, src, all_src, e):
        ImgViewer(src, all_src)