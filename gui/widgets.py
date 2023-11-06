import os
import sys
import tkinter

from cfg import cnf

from .utils import *
import customtkinter

__all__ = (
    "CScroll",
    "CSep",
    "CButton",
    "CFrame",
    "RFrame",
    "CLabel",
    "CWindow",
    "SmbAlert",
    "MacMenu",
    "Context",
    )


class RFrame(customtkinter.CTkFrame):
    def __init__(
            self, master, corner_radius=3, fg_color=cnf.dgray_color, **kw):
        super().__init__(
            master, corner_radius=corner_radius, fg_color=fg_color, **kw)


class CScroll(customtkinter.CTkScrollableFrame):
    def __init__(self, master: tkinter, fg_color=cnf.bg_color, **kw):
        super().__init__(master, fg_color=fg_color, **kw)
        self._scrollbar.configure(width=15)

    def moveup(self, e=None):
        try:
            self._parent_canvas.yview_moveto("0.0")
        except Exception as e:
            print("widgets > CScroll > cant move up")
            print(e)

    def scroll_width(self):
        return self._scrollbar.winfo_reqwidth()
    
    def get_parrent(self):
        return self._parent_canvas


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter, bg=cnf.btn_color, height=1, **kw):
        super().__init__(master, bg=bg, height=height, **kw)


class CButton(customtkinter.CTkButton):
    def __init__(
            self, master: tkinter,
            text_color=cnf.fg_color, fg_color=cnf.btn_color,
            corner_radius=3, width=75,
            hover=0, border_spacing=2,
            font=("San Francisco Pro", 13, "normal"),
            **kw,
            ):

        super().__init__(
            master,
            text_color=text_color, fg_color=fg_color,
            corner_radius=corner_radius, width=width,
            hover=hover, border_spacing=border_spacing,
            font=font, 
            **kw
            )

    def cmd(self, cmd):
        self.bind("<ButtonRelease-1>", cmd)

    def uncmd(self):
        self.unbind("<ButtonRelease-1>")


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, bg=cnf.bg_color, **kwargs):
        super().__init__(master, bg=bg, **kwargs)


class CLabel(tkinter.Label):
    def __init__(
            self, master, bg=cnf.bg_color, fg=cnf.fg_color,
            font=("San Francisco Pro", 13, "normal"), **kwargs
            ):
        super().__init__(master, bg=bg, fg=fg, font=font, **kwargs)


class CWindow(tkinter.Toplevel):
    def __init__(self, bg=cnf.bg_color, padx=15, pady=15, **kwargs):
        super().__init__(bg=bg, padx=padx, pady=pady, **kwargs)
        self.bind("<Command-q>", on_exit)
        self.resizable(0,0)


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()
        self.minsize(420, 85)
        self.protocol("WM_DELETE_WINDOW", self.close_smb)
        self.bind("<Escape>", self.close_smb)
        place_center(cnf.root, self, 420, 85)

        txt = cnf.lng.no_connection
        title_lbl = CLabel(
            self, text=txt, font=("San Francisco Pro", 22, "bold")
            )
        title_lbl.pack()

        txt2 = cnf.lng.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify="left")
        descr_lbl.pack(padx=15, pady=(0, 5))

        cnf.root.update_idletasks()
        self.grab_set_global()

    def close_smb(self, e=None):
        self.destroy()
        cnf.root.focus_force()


class MacMenu(tkinter.Menu):
    def __init__(self):
        menubar = tkinter.Menu(cnf.root)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            cnf.root.createcommand("tkAboutDialog", self.about_dialog)

        cnf.root.configure(menu=menubar)

    def about_dialog(self):
        try:
            cnf.root.tk.call("tk::mac::standardAboutPanel")
        except Exception:
            print("no dialog panel")


class Context(tkinter.Menu):
    def __init__(self):
        super().__init__()

    def sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event, ismenu=None):
        try:
            self.tk_popup(e.x_root, e.y_root)
        finally:
            self.grab_release()
        
    def do_popup_menu(self, e: tkinter.Event, btn, collname):
        try:
            btn.configure(fg_color=cnf.blue_color)
            self.tk_popup(e.x_root, e.y_root)
        finally:
            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.lgray_color)
            else:
                btn.configure(fg_color=cnf.bg_color_menu)
            self.grab_release()

    def imgview(self, img_src, all_src):
        from .img_viewer import ImgViewer
        self.add_command(
            label=cnf.lng.view,
            command=lambda: ImgViewer(img_src, all_src)
            )

    def imginfo(self, parrent: tkinter.Toplevel, img_src):
        from .img_info import ImageInfo
        self.add_command(
            label=cnf.lng.info,
            command=lambda: ImageInfo(parrent, img_src)
            )

    def reveal_jpg(self, img_src):
        self.add_command(
            label=cnf.lng.find_jpg,
            command=lambda: finder_actions(img_src, reveal=True)
            )

    def reveal_tiffs(self, img_src):
        self.add_command(
            label=cnf.lng.find_tiff,
            command=lambda: finder_actions(img_src, tiff=True, reveal=True)
            )

    def pastesearch(self):
        self.add_command(
            label=cnf.lng.paste,
            command=paste_search
            )

    def clear(self):
        self.add_command(
            label=cnf.lng.clear,
            command=lambda: cnf.search_var.set("")
            )

    def download_onefile(self, img_src):
        self.add_command(
            label=(
                f"{cnf.lng.copy} jpg {cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(img_src, download=True)
            )

    def download_tiffs(self, img_src):
        self.add_command(
            label=(
                f"{cnf.lng.copy} tiff {cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(img_src, tiff=True, download=True)
            )

    def reveal_coll(self, collname):
        self.add_command(
            label=cnf.lng.reveal_coll,
            command=lambda: reveal_coll(collname)
            )

    def show_coll(self, e: tkinter.Event, btn, collname):
        self.add_command(
            label=cnf.lng.view,
            command=lambda: cnf.show_coll(e, btn, collname)
            )
        
    def copy_tiffs_paths(self, img_src):
        self.add_command(
            label=cnf.lng.copy_path_tiff,
            command=lambda: finder_actions(img_src, tiff=True, copy_path=True)
            )
        
    def copy_jpg_path(self, img_src):
        self.add_command(
            label=cnf.lng.copy_path_jpg,
            command=lambda: finder_actions(img_src, copy_path=True),
            
            )

    def db_remove_img(self, img_src):
        self.add_command(
            label=cnf.lng.remove_fromapp,
            command=lambda: db_remove_img(img_src)
            )

    def download_group(self, title, paths_list):
        self.add_command(
            label=(
                f"{cnf.lng.copy} jpg\n"
                f"{cnf.lng.from_pretext} \"{title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(paths_list, download=True),
            
        )

    def download_group_tiffs(self, title, paths_list):
        self.add_command(
            label=(
                f"{cnf.lng.copy} tiff\n"
                f"{cnf.lng.from_pretext} \"{title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=(
                lambda: finder_actions(paths_list, tiff=True, download=True)
                )
                )
        
    def copy_text(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy,
            command=lambda: copy_text(e.widget.copy)
            )

    def copy_all(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_all,
            command=lambda: copy_text(e.widget.get("1.0",tkinter.END))
            )

    def download_fullsize(self, img_src):
        self.add_command(
            label=cnf.lng.fullsize,
            command=lambda: finder_actions(img_src, tiff=True, fullsize=True)
            )

    def download_group_fullsize(self, title, paths_list):
        self.add_command(
            label=(
                f"{cnf.lng.group_fullsize}\n"
                f"{cnf.lng.from_pretext} \"{title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=(
                lambda: finder_actions(paths_list, tiff=True, fullsize=True)
                )
                )
        
    def apply_filter(self, e: tkinter.Event, label, filter, collname=None):
        self.add_command(
            label=label,
            command=lambda: apply_filter(e, filter, collname)
            )
