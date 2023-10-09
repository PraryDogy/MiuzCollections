import tkinter
from datetime import datetime


class Globals:
    """
    reload menu: menu > Menu().reload_menu()
    reload_thumbs: thumbnails > Thumbnails().reload_thumbs()
    reload_scroll: thumbnails > Thumbnails().reload_scroll()
    show_coll: menu > Menu().show_coll()
    set_calendar_title: filter > Filter().set_calendar_title()
    stbar_btn: stbar > StBar().upd_btn tkinter label
    search_var: thumbnails > ThumbsSearch()
    start: datetime.datetime
    end: datetime.datetime
    named start, named end: datetime as readable text
    """
    reload_menu = None # menu > Menu().reload_menu()
    reload_thumbs = None # thumbnails > Thumbnails().reload_thumbs()
    reload_scroll = None # thumbnails > Thumbnails().reload_scroll()
    show_coll = None # menu > Menu().show_coll()
    set_calendar_title = None # filter > Filter().set_calendar_title()
    stbar_btn = tkinter.Label # stbar > StBar().upd_btn tkinter label
    search_var = tkinter.StringVar(value="") # thumbnails > ThumbsSearch()

    start: datetime = None
    end: datetime = None
    named_start: str = None # datetime as readable text
    named_end: str = None # datetime as readable text
