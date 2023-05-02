from . import cfg, place_center, tkinter, filedialog
from .widgets import CButton, CFrame, CLabel, CWindow


class ScanerGui(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title("Сканер")

        self.geometry(f'{cfg.config["ROOT_W"]-180}x{cfg.config["ROOT_H"]-180}')

        self.load_main_widget().pack()

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def load_main_widget(self):
        parent = CFrame(self)

        lbl = CLabel(parent, text = "Сканер")
        lbl.configure(font=('San Francisco Pro', 45, 'bold'))
        lbl.pack()

        lbl = CLabel(
            parent,
            text = (
            "Я покажу, каких фотографий нет в коллекциях."
            ),
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            )
        lbl.pack(anchor=tkinter.W)

        path_widget = CLabel(
            parent,
            text = "Нажмите 'Обзор' и выберите папку",
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            wraplength = 370,
            )
        path_widget.pack(anchor=tkinter.W)

        select_path = CButton(parent, text = 'Обзор')
        select_path.pack(pady = (15, 0), padx = (5, 0))
        select_path.configure(width = 9)
        select_path.cmd(lambda e, x = path_widget: self.select_path(x))

        return parent

    def select_path(self, master: tkinter.Label):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        master['text'] = path