import tkinter
from datetime import datetime


class Globals:
    reload_menu = None #reload left menu
    reload_thumbs = None #reload thumbnails grid without scroll
    reload_scroll = None #reload thumbnails grid with scroll
    filter_text_cmd = None #change title text in filter window under calendars
    stbar_btn = tkinter.Label #status bar button
    search_var = tkinter.StringVar(value="")

    start: datetime = None
    end: datetime = None
    named_start = None
    named_end = None