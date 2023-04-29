import tkinter
import cfg
from .img_viewer import ImgViewer
from . import find_tiff, find_jpeg


class ThumbnailsMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Label, src: str, all_src: list):
        tkinter.Menu.__init__(self, master, tearoff = 0)

        self.add_command(
            label = "Просмотр",
            command = lambda: self.preview(src, all_src)
            )

        self.add_separator()

        self.add_command(
            label = "Показать в Finder",
            command = lambda: self.find_jpeg(src)
            )

        self.add_command(
            label = "Показать tiff",
            command = lambda: self.find_tiff(src)
            )

        master.bind("<Button-2>", self.do_popup)

    def do_popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()

    def preview(self, src, all_src):
        ImgViewer(src, all_src)

    def find_jpeg(self, src):
        find_jpeg(src)

    def find_tiff(self, src):
        find_tiff(src)