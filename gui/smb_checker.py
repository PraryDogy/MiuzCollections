import tkinter

import cfg
from utils import MyButton, MyLabel, place_center


class SmbChecker(tkinter.Toplevel):
    """
    Gui for utils smb_check
    """
    def __init__(self):
        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, padx=10, pady=10)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())

        self.focus_force()
        self.title('Нет подключения')
        self.resizable(0,0)

        txt = 'Нет подключения к сетевому диску Miuz. '
        title_lbl = MyLabel(
            self, text=txt, font=('Arial', 22, 'bold'), wraplength=350)
        title_lbl.pack(pady=(10, 20), padx=20)

        txt2 =(
            '- Проверьте подключение к интернету. '
            '\n\n- Откройте любую папку на сетевом диске,'
            '\nвведите логин и пароль, если требуется'
            '\n\n- Откройте настройки > дополнительно, введите'
            '\nправильный путь до галерии изображений'
            '\nи перезапустите приложение.'
            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = MyLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 15))

        cls_btn = MyButton(self, text='Закрыть')
        cls_btn.cmd(lambda e: self.destroy())
        cls_btn.pack()

        place_center(self)
        self.deiconify()
        self.grab_set()
