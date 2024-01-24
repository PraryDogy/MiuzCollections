import abc
import sys
import tkinter

try:
    from typing_extensions import Callable, Literal
except ImportError:
    from typing import Literal, Callable

import customtkinter

from cfg import cnf
from utils import SysUtils

__all__ = (
    "CEntry",
    "CScroll",
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "MacMenu",
    )


class BaseCWid(abc.ABC):
    @abc.abstractmethod
    def get_parrent(self):
        pass


class CEntry(customtkinter.CTkEntry, BaseCWid):
    def __init__(self, master: tkinter, width: int = 200,
                 corner_radius: int = cnf.corner, border_width: int = 0,
                 fg_color: str = cnf.btn_color,
                 justify: Literal["left", "right", "center"] = "left",
                 textvariable: tkinter.Variable = None,
                 **kwargs):

        customtkinter.CTkEntry.__init__(
            self, master=master, width=width,corner_radius=corner_radius,
            border_width=border_width, fg_color=fg_color, justify=justify,
            textvariable=textvariable, **kwargs)
        
    def get_parrent(self):
        return self._canvas


class CScroll(customtkinter.CTkScrollableFrame, BaseCWid, SysUtils):
    def __init__(self, master: tkinter, width: int = 200,
                 corner_radius: int = 0, fg_color: str = cnf.bg_color,
                 scroll_width: int = cnf.scroll_width,
                 scroll_color: str = None):

        customtkinter.CTkScrollableFrame.__init__(
            self, master=master, width=width, corner_radius=corner_radius,
            fg_color=fg_color)

        self._scrollbar.configure(width=scroll_width)

        if scroll_color:
            self._scrollbar.configure(button_color=scroll_color)

    def set_scroll_speed(self, scroll_speed: int):
        self._parent_canvas.configure(yscrollincrement=scroll_speed)

    def get_parrent(self):
        return self._parent_canvas

    def moveup(self, e=None):
        try:
            self.get_parrent().yview_moveto("0.0")
        except Exception:
            self.print_err()


class CSep(tkinter.Frame, BaseCWid):
    def __init__(self, master: tkinter, bg: str = cnf.btn_color,
                 height: int = 1, **kw):

        tkinter.Frame.__init__(self, master=master, bg=bg, height=height, **kw)

    def get_parrent(self):
        return self


class CButton(customtkinter.CTkButton, BaseCWid):
    def __init__(self, master: tkinter, text_color: str = cnf.fg_color,
                 fg_color: str = cnf.btn_color, corner_radius: int = cnf.corner,
                 width: int = 75, hover: bool = 0, border_spacing: int = 2,
                 anchor="center",
                 font: tuple[str, int, str] = ("San Francisco Pro", 13, "normal"),
                 **kw):

        customtkinter.CTkButton.__init__(
            self, master=master, text_color=text_color, fg_color=fg_color,
            corner_radius=corner_radius, width=width, hover=hover,
            border_spacing=border_spacing, font=font, anchor=anchor, **kw)

    def get_parrent(self):
        return self._canvas

    def cmd(self, cmd: Callable):
        self.bind(sequence="<ButtonRelease-1>", command=cmd)

    def uncmd(self):
        self.unbind(sequence="<ButtonRelease-1>")


class CFrame(tkinter.Frame, BaseCWid):
    def __init__(self, master: tkinter, bg: str = cnf.bg_color, **kwargs):
        tkinter.Frame.__init__(self, master=master, bg=bg, **kwargs)

    def get_parrent(self):
        return self


class CLabel(tkinter.Label, BaseCWid):
    def __init__(self, master: tkinter, bg: str = cnf.bg_color,
                 fg: str = cnf.fg_color, text: str = None,
                 font: tuple[str, int, str] = ("San Francisco Pro", 13, "normal"),
                 **kwargs):

        tkinter.Label.__init__(self, master=master, bg=bg, fg=fg, font=font,
                               text=text, **kwargs)

    def get_parrent(self):
        return self


class CWindow(tkinter.Toplevel, BaseCWid):
    def __init__(self, bg: str = cnf.bg_color,
                 padx: int | tuple[int, int] = 15,
                 pady: int | tuple[int, int] = 15, **kwargs):

        tkinter.Toplevel.__init__(self, bg=bg, padx=padx, pady=pady, **kwargs)
        self.resizable(width=0, height=0)

    def get_parrent(self):
        return self

    def place_center(self, w: int, h: int, below_win: tkinter.Toplevel = cnf.root):
        x, y = below_win.winfo_x(), below_win.winfo_y()
        xx = x + below_win.winfo_width() // 2 - w // 2
        yy = y + below_win.winfo_height() // 2 - h // 2
        self.geometry(f"+{xx}+{yy}")




class MacMenu(tkinter.Menu, SysUtils):
    def __init__(self):
        menubar = tkinter.Menu(cnf.root)
        tkinter.Menu.__init__(self, master=menubar)

        if sys.version_info.minor < 10:
            cnf.root.createcommand("tkAboutDialog", self.about_dialog)

        cnf.root.configure(menu=menubar)

    def about_dialog(self):
        try:
            cnf.root.tk.call("tk::mac::standardAboutPanel")
        except Exception:
            self.print_err()
