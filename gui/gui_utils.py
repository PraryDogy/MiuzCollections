import tkinter

class GlobGui:
    _reload_menu = None #reload left menu
    _reload_thumbs = None #reload thumbnails grid without scroll
    _reload_thumbs_scroll = None #reload thumbnails grid with scroll
    _cals_titles_cmd = None #change title text in filter window under calendars
    st_bar_btn = tkinter.Label #status bar button
    str_var = tkinter.StringVar(value="")

    def reload_menu(self):
        __class__._reload_menu()
    
    def reload_thumbs(self):
        __class__._reload_thumbs()

    def reload_thumbs_scroll(self):
        __class__._reload_thumbs_scroll()
    
    def cals_titles_cmd(self):
        __class__._cals_titles_cmd()