import math
import tkinter
import traceback
from datetime import datetime

try:
    from typing_extensions import Callable, Literal, Dict
except ImportError:
    from typing import Callable, Literal, Dict

import sqlalchemy
from PIL import Image, ImageTk

from cfg import cnf
from database import Dbase, ThumbsMd

from .context import *
from .img_viewer import ImgViewer
from .utils import *
from .widgets import *

__all__ = (
    "Thumbs",
    )


class ContextFilter(Context):
    def __init__(self, e: tkinter.Event):
        Context.__init__(self)

        for k, v in cnf.lng.filter_names.items():
            self.apply_filter_thumbs(label=v, filter=k)

        self.apply_filter_thumbs(label=cnf.lng.show_all, filter="all")
        self.do_popup(e=e)


class ContextTitles(Context):
    def __init__(self, e: tkinter.Event, title: str,
                 path_list: tuple[Literal["image path"], ...]):

        Context.__init__(self)
        self.download_group(title=title, paths_list=path_list)

        self.sep()
        self.download_group_tiffs(title=title, paths_list=path_list)

        self.sep()
        self.download_group_fullsize(title=title, paths_list=path_list)

        self.do_popup(e=e)


class ContextAdvanced(Context):
    def __init__(self, e: tkinter.Event, img_src: Literal["image path"]):
        Context.__init__(self)
        self.db_remove_img(img_src=img_src)
        self.do_popup(e=e)


class ContextThumbs(Context):
    def __init__(self, e: tkinter.Event, img_src: Literal["image path"]):
        Context.__init__(self)

        self.imgview(img_src=img_src)
        self.imginfo(parrent=e.widget.winfo_toplevel(), img_src=img_src)

        self.sep()
        self.copy_jpg_path(img_src=img_src)
        self.reveal_jpg(img_src=img_src)
        self.download_jpg(img_src=img_src)

        self.sep()
        self.copy_tiff_path(img_src=img_src)
        self.reveal_tiff(img_src=img_src)
        self.download_tiff(img_src=img_src)

        self.sep()
        self.download_fullsize(img_src=img_src)

        self.do_popup(e=e)


class ThumbsDict(dict):
    def __init__(self) -> dict[str, tuple]:
        """
        dict key: str(month year)
        dict value: list of tuples(PIL Image, image path)
        """
        super().__init__()
        data = Dbase.conn.execute(self.get_query()).fetchall()
        decoded = self.decode_thumbs(thumbs_raw=data)
        self.update(self.create_thumbs_dict(thumbs_raw=decoded))

    def decode_thumbs(
            self,
            thumbs_raw: tuple[tuple[bytes, str, int], ...]
            ) -> tuple[tuple[bytes, str, int], ...]:
        result = []
        for blob, src, modified in thumbs_raw:
            try:
                decoded = decode_image(img=blob)
                cropped = crop_image(img=decoded)
                img = convert_to_rgb(img=cropped)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(
            self,
            thumbs_raw: tuple[tuple[bytes, str, int], ...]) -> dict:
        thumbs_dict = {}

        for img, src, modified in thumbs_raw:
            date_key = datetime.fromtimestamp(modified).date()

            if not any((cnf.start, cnf.end)):
                date_key = f"{cnf.lng.months[date_key.month]} {date_key.year}"
            else:
                date_key = f"{cnf.named_start} - {cnf.named_end}"

            thumbs_dict.setdefault(date_key, [])
            thumbs_dict[date_key].append((img, src))

        return thumbs_dict

    def stamp_dates(self) -> tuple[datetime, datetime]:
        start = datetime.combine(date=cnf.start, time=datetime.min.time())
        end = datetime.combine(date=cnf.end,
                               time=datetime.max.time().replace(microsecond=0))
        return (datetime.timestamp(start), datetime.timestamp(end))

    def get_query(self):
        q = sqlalchemy.select(ThumbsMd.img150, ThumbsMd.src, ThumbsMd.modified)

        search = cnf.search_var.get()
        if search:
            search.replace("\n", "").strip()
            q = q.filter(ThumbsMd.src.like(f"%{search}%"))

        if cnf.curr_coll != cnf.all_colls:
            q = q.filter(ThumbsMd.collection == cnf.curr_coll)

        filters = []
        for k, v in cnf.filter_true_names.items():
            if cnf.filter_values[k]:
                if cnf.filter_true_names[k]:
                    examp = f"%/{cnf.filter_true_names[k]}/%"
                    filters.append(ThumbsMd.src.like(examp))
        filters = sqlalchemy.or_(*filters)

        other_filter = []
        if cnf.filter_values["other"]:
            for k, v in cnf.filter_true_names.items():
                examp = f"%/{cnf.filter_true_names[k]}/%"
                other_filter.append(ThumbsMd.src.not_like(examp))
        other_filter = sqlalchemy.and_(*other_filter)

        if any((str(filters), str(other_filter))):
            q = q.filter(sqlalchemy.or_(filters, other_filter))

        if not any((cnf.start, cnf.end)):
            q = q.limit(cnf.limit)
        else:
            t = self.stamp_dates()
            q = q.filter(ThumbsMd.modified > t[0])
            q = q.filter(ThumbsMd.modified < t[1])

        q = q.order_by(-ThumbsMd.modified)
        return q


class ResetDatesBtn(CButton):
    def __init__(self, master: tkinter):
        CButton.__init__(self, master=master, text=cnf.lng.reset_dates)
        self.cmd(self.reset_dates_cmd)

    def reset_dates_cmd(self, e: tkinter.Event):
        cnf.start, cnf.end = None, None
        cnf.reload_filters()
        cnf.reload_scroll()


class ResetSearchBtn(CButton):
    def __init__(self, master: tkinter):
        CButton.__init__(self, master=master, text=cnf.lng.reset_search)
        self.cmd(self.reset_search_cmd)

    def reset_search_cmd(self, e: tkinter.Event):
        cnf.search_var.set(value="")
        cnf.reload_scroll()


class ResetFiltersBtn(CButton):
    def __init__(self, master: tkinter):
        CButton.__init__(self, master=master, text=cnf.lng.show_all)
        self.cmd(self.reset_filters_cmd)

    def reset_filters_cmd(self, e: tkinter.Event):
        for k, v in cnf.filter_values.items():
            cnf.filter_values[k] = False
        cnf.reload_filters()
        cnf.reload_scroll()


class NoImages(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        str_var = cnf.search_var.get()
        no_images = CLabel(master=self, text=cnf.lng.no_photo,
                           font=("San Francisco Pro", 18, "bold"))
        no_images.pack(pady=(15, 0))

        if str_var:
            noimg_t = (f"{cnf.lng.no_photo} {cnf.lng.with_name}"
                       f"\n\"{str_var}\"")
            no_images.configure(text=noimg_t)
            ResetSearchBtn(master=self).pack(pady=(15, 0))

        elif any((cnf.start, cnf.end)):
            noimg_t = (f"{cnf.lng.no_photo}"
                       f"\n{cnf.named_start} - {cnf.named_end}")
            no_images.configure(text=noimg_t)
            ResetDatesBtn(master=self).pack(pady=(15, 0))

        else:
            filters = (f"\"{cnf.lng.filter_names[k].lower()}\""
                       for k, v in cnf.filter_values.items()
                       if v)
            filters = ",  ".join(filters)
            noimg_t = (f"{cnf.lng.no_photo_filter}\n{filters}")
            no_images.configure(text=noimg_t)
            ResetFiltersBtn(master=self).pack(pady=(15, 0))


class AboveThumbs(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        if any((cnf.start, cnf.end)):
            ResetDatesBtn(master=self).pack(pady=(15, 0))
        elif cnf.search_var.get():
            ResetSearchBtn(master=self).pack(pady=(15, 0))


class ImgGridTitle(CLabel):
    def __init__(self, master: tkinter, title: str,
                 img_src_list: tuple[str, ...],
                 font=("San Francisco Pro", 18, "bold")):

        text = f"{title}, {cnf.lng.total}: {len(img_src_list)}"
        if cnf.search_var.get():
            text = (
                f"{cnf.lng.photo} {cnf.lng.with_name} "
                f"\"{cnf.search_var.get()}\"\n{text}"
                )

        CLabel.__init__(self, master=master, text=text, font=font, anchor="w",
                         justify="left")

        self.bind(sequence="<ButtonRelease-2>", func=lambda e:
                  ContextTitles(e=e, title=title, paths_list=img_src_list))


class ImgGrid(CLabel):
    def __init__(self, master: tkinter, grid_w: int, grid_h: int,
                 thumbsize: Literal["cnf.thumbsize + cnf.thumbspad"],
                 bg=cnf.bg_color, fg=cnf.fg_color, anchor="w"):

        CLabel.__init__(self, master=master, bg=bg, fg=fg, anchor=anchor)

        self.bind(sequence="<ButtonRelease-1>", func=self.__click)
        self.bind(sequence="<ButtonRelease-2>", func=self.__r_click)
        self.bind(sequence="<Command-ButtonRelease-2>", func=self.__r_cmd_click)

        self.__empty_grid = Image.new(mode="RGBA", size=(grid_w, grid_h),
                                      color=bg)
        self.__coords = {}
        self.__thumbsize = thumbsize

    def set_tk_img(self):
        img = ImageTk.PhotoImage(image=self.__empty_grid)
        self.configure(image=img)
        self.image_names = img

    def grid_paste(self, img: Image, img_src: str, grid_x: int, grid_y: int):
        self.__empty_grid.paste(im=img, box=(grid_x, grid_y))

        coord = (grid_x // self.__thumbsize, grid_y // self.__thumbsize)
        self.__coords[coord] = img_src
        cnf.all_src.append(img_src)

    def __get_coords(self, e: tkinter.Event) -> Literal["str img src"] | bool:
        try:
            clmn = e.x // self.__thumbsize
            row = e.y // self.__thumbsize
            return self.__coords[(clmn, row)]
        except KeyError:
            return False

    def __click(self, e: tkinter.Event):
        img_src = self.__get_coords(e)
        if img_src:
            ImgViewer(img_src=img_src)

    def __r_cmd_click(self, e: tkinter.Event):
        img_src = self.__get_coords(e)
        if img_src:
            ContextAdvanced(e=e, img_src=img_src)

    def __r_click(self, e: tkinter.Event):
        img_src = self.__get_coords(e=e)
        if img_src:
            ContextThumbs(e=e, img_src=img_src)
        else:
            ContextFilter(e=e)


class Thumbs(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.__resize_task = None
        self.__thumbsize = cnf.thumbsize + cnf.thumbspad
        cnf.root.bind(sequence="<Configure>", func=self.decect_resize)

        self.load_scroll()
        self.load_thumbs()
        self.bind_scroll_thumbs()

    def load_scroll(self):
        self.__scroll_parrent = CFrame(master=self)
        self.__scroll_parrent.pack(expand=1, fill="both")

        self.scroll = CScroll(master=self.__scroll_parrent)
        self.scroll.pack(expand=1, fill="both")

    def load_thumbs(self):
        thumbs_dict = ThumbsDict()

        if thumbs_dict:
            self.__above_thumbs = AboveThumbs(master=self.scroll)
            self.__above_thumbs.pack()
        else:
            self.__above_thumbs = NoImages(master=self.scroll)
            self.__above_thumbs.pack()

        self.__thumbsframe = CFrame(master=self.scroll, width=10)
        self.__thumbsframe.pack(anchor="w", padx=5)

        for i in (self.scroll, self.__thumbsframe, self.__above_thumbs):
            i.bind(sequence="<ButtonRelease-2>", func=ContextFilter)

        grid_limit = 500
        self.__clmns = self.get_clmns_count()
        grid_w = self.__clmns * self.__thumbsize

        for x, (date_key, img_list) in enumerate(thumbs_dict.items()):
            chunks = [img_list[i:i + grid_limit]
                      for i in range(0, len(img_list), grid_limit)]

            grid_title = ImgGridTitle(
                master=self.__thumbsframe, title=date_key,
                img_src_list=[i[1] for i in img_list])
            grid_title_pad = 30 if x != 0 else 15
            grid_title.pack(anchor="w", pady=(grid_title_pad, 0),
                            padx=(cnf.thumbspad, 0))

            for chunk in chunks:
                rows = math.ceil(len(chunk) / self.__clmns)
                grid_h = rows * self.__thumbsize
                grid_x, grid_y = 0, 0

                grid_img = ImgGrid(master=self.__thumbsframe,
                                   grid_w=grid_w, grid_h=grid_h,
                                   thumbsize=self.__thumbsize)
                grid_img.pack(anchor="w")

                for img_num, (img_obj, img_src) in enumerate(iterable=chunk, start=1):

                    grid_img.grid_paste(img=img_obj, img_src=img_src,
                                        grid_x=grid_x, grid_y=grid_y)

                    grid_x = grid_x + self.__thumbsize

                    if img_num % self.__clmns == 0:
                        grid_y = grid_y + self.__thumbsize
                        grid_x = 0

                grid_img.set_tk_img()

        ln_thumbs = len([item for val in thumbs_dict.values() for item in val])

        if ln_thumbs == cnf.limit:
            more_btn = CButton(master=self.__thumbsframe, text=cnf.lng.show_more)
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=15)

    def bind_scroll_thumbs(self):
        for i in (self.__scroll_parrent, self.scroll, self.__thumbsframe,
                  *self.__thumbsframe.winfo_children()):
            self.scroll.set_scrolltag(tag="thumbs_scroll", widget=i.get_parrent())
        self.scroll.bind_autohide_scroll(tag="thumbs_scroll")

    def show_more_cmd(self):
        cnf.limit += 150
        cnf.reload_thumbs()

    def decect_resize(self, e: tkinter.Event):
        if self.__resize_task:
            cnf.root.after_cancel(id=self.__resize_task)
        self.__resize_task = cnf.root.after(ms=500, func=self.thumbs_resize)

    def thumbs_resize(self):
        if cnf.root.winfo_width() != cnf.root_g["w"]:
            if self.__clmns != self.get_clmns_count():

                cnf.root_g.update({"w": cnf.root.winfo_width(),
                                   "h": cnf.root.winfo_height()})
                cnf.reload_thumbs()

    def reload_scroll(self):
        for i in (self.__scroll_parrent, self.scroll):
            i.destroy()
        cnf.all_src.clear()
        self.load_scroll()
        self.load_thumbs()
        self.bind_scroll_thumbs()
        cnf.root.focus_force()

    def reload_thumbs(self):
        for i in (self.__above_thumbs, self.__thumbsframe):
            i.destroy()
        cnf.all_src.clear()
        self.load_thumbs()
        cnf.root.focus_force()

    def get_clmns_count(self) -> int:
        w = cnf.root.winfo_width() - cnf.menu_w - cnf.scroll_width
        return w // self.__thumbsize
