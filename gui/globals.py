import tkinter
from datetime import datetime


class Globals:
    reload_menu = None # menu > Menu().reload_menu()
    reload_thumbs = None # thumbnails > Thumbnails().reload_thumbs()
    reload_scroll = None # thumbnails > Thumbnails().reload_scroll()
    show_coll = None # menu > Menu().show_coll()
    set_calendar_title = None # filter > Filter().set_calendar_title()
    stbar_btn = tkinter.Label # stbar > StBar.upd_btn
    search_var = tkinter.StringVar(value="")

    start: datetime = None
    end: datetime = None
    named_start = None
    named_end = None