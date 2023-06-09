from . import (Image, calendar, conf, datetime, get_coll_name, on_exit, os,
               partial, place_center, sys, tkinter, re)

__all__ = (
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "SmbAlert",
    "ImageInfo",
    "MacMenu",
    "CCalendar",
    "focus_last",
    )


def focus_last():
    for k, v in conf.root.children.items():
        if isinstance(v, CWindow):
            v.focus_force()
            return
    conf.root.focus_force()


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if not kw:
            self.configure(bg=conf.btn_color, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=conf.btn_color, fg=conf.fg_color, width=11, height=1,
            font=("San Francisco Pro", 13, "normal"))

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=conf.sel_color)
        conf.root.after(100, lambda: self.configure(bg=conf.btn_color))


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=conf.bg_color)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=conf.bg_color,
            fg=conf.fg_color,
            font=("San Francisco Pro", 13, "normal"),
            )


class CWindow(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        conf.root.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Command-w>', self.close_win)
        self.bind('<Escape>', self.close_win)

        self.bind('<Command-q>', on_exit)

        self.resizable(0,0)
        self.configure(bg=conf.bg_color, padx=15, pady=15)

    def close_win(self, e=None):
        self.destroy()
        focus_last()


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()

        txt = conf.lang.smb_title
        title_lbl = CLabel(
            self, text=txt, font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack(pady=(0, 5), padx=20)

        txt2 = conf.lang.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT, )
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text=conf.lang.close)
        btn.cmd(self.btn_cmd)
        btn.pack()

        conf.root.update_idletasks()
        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def btn_cmd(self, e=None):
        self.destroy()
        focus_last()


class ImageInfo(CWindow):
    def __init__(self, src: str):
        under_win = None

        for k, v in conf.root.children.items():
            if isinstance(v, CWindow):
                under_win = v

        if not under_win:
            under_win = conf.root

        super().__init__()

        self.title(conf.lang.info)
        self.geometry("400x110")
        self.minsize(400, 110)
        self.maxsize(800, 150)
        self.configure(padx=5, pady=5)
        self.resizable(1, 1)

        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        frame = CFrame(self)
        frame.pack(expand=True, fill="both")

        labels = {
            conf.lang.info_collection: get_coll_name(src),
            conf.lang.info_filename: name,
            conf.lang.info_chanded: filemod,
            conf.lang.info_resolution: f"{w}x{h}",
            conf.lang.info_size: f"{filesize}мб",
            conf.lang.info_path: src,
            }

        left_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.keys()),
            justify = tkinter.RIGHT,
            anchor = tkinter.E,
            )
        left_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        right_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.values()),
            justify = tkinter.LEFT,
            anchor = tkinter.W,
            )
        right_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Command-w>', self.close_win)
        self.bind('<Escape>', self.close_win)

        conf.root.update_idletasks()

        x, y = under_win.winfo_x(), under_win.winfo_y()
        xx = x + under_win.winfo_width()//2 - self.winfo_width()//2
        yy = y + under_win.winfo_height()//2 - self.winfo_height()//2

        self.geometry(f'+{xx}+{yy}')

        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_win(self, e=None):
        self.destroy()
        focus_last()


class MacMenu(tkinter.Menu):
    def __init__(self):
        menubar = tkinter.Menu(conf.root)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            conf.root.createcommand('tkAboutDialog', self.about_dialog)

        conf.root.configure(menu=menubar)

    def about_dialog(self):
        try:
            conf.root.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")


class CCalendarEntry(CWindow):
    def cust_date_win(self, e=None):
        self.win_cust = CWindow()
        self.win_cust.title(conf.lang.cust_title)
        self.win_cust.protocol("WM_DELETE_WINDOW", self.cust_can_cmd)
        self.win_cust.bind('<Command-w>', self.cust_can_cmd)
        self.win_cust.bind('<Escape>', self.cust_can_cmd)
        self.bind('<Command-q>', on_exit)
        # self.bind_all("<ButtonRelease-1>", self.g_click)

        cust_l = CLabel(self.win_cust, text=conf.lang.cust_l)
        cust_l.pack(pady=(0, 5))

        var_t = f"{self.dd}.{self.mm}.{self.yy}"
        var = tkinter.StringVar(value=var_t)
        self.cust_ent = tkinter.Entry(
            self.win_cust,
            width=15,
            textvariable=var,
            bg=conf.ent_color,
            insertbackground="white",
            fg=conf.fg_color,
            highlightthickness=0,
            justify="center",
            selectbackground=conf.btn_color,
            border=1
            )
        self.cust_ent.pack(ipady=2)
        var.trace("w", lambda *args: self.character_limit(var))
        self.cust_ent.icursor(10)
        self.cust_ent.selection_range(0, "end")

        btns = CFrame(self.win_cust)
        btns.pack(pady=(15, 0))

        self.ok = CButton(btns, text=conf.lang.ok)
        self.ok.configure(fg=conf.hov_color)
        self.ok.pack(side="left", padx=(0, 15))

        self.cancel = CButton(btns, text=conf.lang.cancel)
        self.cancel.pack(side="left")
        self.cancel.bind("<ButtonRelease-1>", self.cust_can_cmd)

        conf.root.update_idletasks()

        under_win = self.winfo_toplevel()
        x, y = under_win.winfo_x(), under_win.winfo_y()
        xx = x + under_win.winfo_width()//2 - self.win_cust.winfo_width()//2
        yy = y + under_win.winfo_height()//2 - self.win_cust.winfo_height()//2
        self.win_cust.geometry(f'+{xx}+{yy}')

        self.win_cust.deiconify()
        self.win_cust.wait_visibility()
        self.win_cust.grab_set_global()
        self.cust_ent.focus_force()

    def g_click(self, e:tkinter.Event=None):
        try:
            if e.widget.widgetName != "entry":
                e.widget.focus()
        except AttributeError:
            print("entry click error")

    def character_limit(self, e:tkinter.StringVar):
        t = e.get()
        try:
            self.cust_date = datetime.strptime(t, '%d.%m.%Y')
            self.ok.configure(fg=conf.fg_color)
            self.ok.bind("<ButtonRelease-1>", self.cust_ok_cmd)
            self.win_cust.bind("<Return>", self.cust_ok_cmd)
        except ValueError:
            self.ok.configure(fg=conf.hov_color)
            self.ok.unbind("<ButtonRelease-1>")
            self.win_cust.unbind("<Return>")

            if len(t) > 10:
                e.set(t[:10])

    def cust_ok_cmd(self, e=None):
        self.clicked = True

        self.yy, self.mm, self.dd = tuple(self.cust_date.timetuple())[:3]

        try:
            self.change_title()
            self.set_my_date()
            self.fill_days()
        except tkinter.TclError:
            print("enter custom date widgets calendar error title change")

        self.win_cust.destroy()
        self.winfo_toplevel().grab_set_global()
        self.winfo_toplevel().focus_force()

    def cust_can_cmd(self, e=None):
        self.unbind_all("<ButtonRelease-1>")
        self.win_cust.destroy()
        self.winfo_toplevel().grab_set_global()
        self.winfo_toplevel().focus_force()


class CCalendar(CFrame, CCalendarEntry):
    def __init__(self, master, input: datetime):
        super().__init__(master)

        if input:
            self.yy, self.mm, self.dd = tuple(input.timetuple())[:3]
        else:
            self.yy, self.mm, self.dd = tuple(datetime.today().timetuple())[:3]

        self.sel_btn: tkinter.Label = None
        self.btns = []
        self.clicked = False

        self.load_calendar().pack()
        self.paint_grid()
        self.change_title()

    def load_calendar(self):
        parrent = CFrame(self)
        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles.pack(pady=5)

        prev_m = CButton(titles, text="<")
        prev_m.configure(width=6, font=f, bg=conf.bg_color)
        prev_m.pack(side="left")
        prev_m.cmd(self.switch_month)

        self.title = CLabel(titles)
        self.title.configure(width=13, font=f)
        self.title.pack(side="left")
        self.title.bind("<ButtonRelease-1>", self.cust_date_win)

        next_m = CButton(titles, text=">")
        next_m.configure(width=6, font=f, bg=conf.bg_color)
        next_m.pack(side="left")
        next_m.cmd(self.switch_month)

        row = CFrame(parrent)
        row.pack()

        for i in conf.lang.calendar_days:
            lbl = CButton(row, text = i)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")

        sep = CSep(parrent)
        sep.configure(bg=conf.bg_color, height=2)
        sep.pack(fill="x")

        row = CFrame(parrent)
        row.pack()

        for i in range(1, 43):
            lbl = CButton(row)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")
            lbl.cmd(self.select_day_click)

            if i % 7 == 0:
                row = CFrame(parrent)
                row.pack(anchor="w")

            self.btns.append(lbl)
        return parrent

    def create_numbers(self):
        first_weekday = datetime.weekday(datetime(self.yy, self.mm, 1))
        month_len = calendar.monthrange(self.yy, self.mm)[1] + 1

        days = [None for i in range(first_weekday)]
        days.extend([i for i in range(1, month_len)])
        days.extend([None for i in range(42 - len(days))])

        return days

    def paint_grid(self):
        today = datetime.today()
        today = bool(
            all(
            (self.yy==today.year, self.mm==today.month)
            )
            )
        for day, btn in zip(self.create_numbers(), self.btns):
            if day:
                btn.configure(text=day, bg=conf.btn_color)
            else:
                btn.configure(text="", bg=conf.bg_color)
            if

    def change_title(self):
        if self.dd:
            t = f"{self.dd} {conf.lang.months_p[self.mm]} {self.yy}"
        else:
            t = f"{conf.lang.months[self.mm]} {self.yy}"
        self.title.configure(text=t)

    def select_day_click(self, e:tkinter.Event = None):
        if self.sel_btn:
            self.sel_btn.configure(bg=conf.btn_color)
        self.sel_btn = e.widget
        self.sel_btn.configure(bg=conf.sel_color)
        self.dd = self.sel_btn["text"]

        self.change_title()
        self.clicked = True

    def switch_month(self, e=None):
        if e.widget["text"] != "<":
            self.mm += 1
        else:
            self.mm -= 1

        if self.mm > 12:
            self.mm = 1
            self.yy += 1

        elif self.mm <1:
            self.mm = 12
            self.yy -= 1
        
        self.dd = None

        self.change_title()
        self.paint_grid()

    def get_date(self):
        if all((self.clicked, self.dd, self.mm, self.yy)):
            return datetime(self.yy, self.mm, self.dd)
        return None
