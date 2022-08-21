import tkinter

import cfg
from Utils.Styled import *
from .GuiGeneral import *

class Create(tkinter.Toplevel):
    def __init__(self):
        """Create tk TopLevel with tkinter.Labels and buttons. 
        Methods: just run class. 
        Imports: ManageDb from DataBase package."""

        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, pady=10)

        self.resizable(0,0)
        self.attributes('-topmost', 'true')
        self.title('Настройки')
        self.propagate(0)
        h = int(cfg.ROOT.winfo_screenheight()*0.6)
        self.configure(height=h, width=600)

        frameL = MyFrame(self)
        frameL.pack(side='left', padx=10)

        frameR = MyFrame(self)
        frameR.configure(height=500, bg='red')
        frameR.pack(side='right', padx=10, fill='y')

        LeftMenu(frameL).pack()

        General(frameR).pack()
        BelowMenu(frameR).pack(anchor='se')

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center') 


class LeftMenu(MyFrame):
    def __init__(self, master):
        super().__init__(master)

        genBtn = MyButton(
            self, lambda event: self.CloseGen(), 'Основные')
        genBtn.configure(bg=cfg.BGPRESSED)
        genBtn.pack()

        expertBtn = MyButton(
            self, lambda event: '', 'Эксперт')
        expertBtn.pack()

    def CloseGen(self):
        rightMenu = self.winfo_toplevel().winfo_children()[1]
        general = rightMenu.winfo_children()[0]
        general.pack_forget()


class General(MyFrame):
    def __init__(self, master):
        super().__init__(master)
        FullScan(self)
        About(self)


class BelowMenu(MyFrame):
    def __init__(self, master):
        super().__init__(master)

        buttonOk = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Ok')
        buttonOk.pack(side='left', padx=10)

        buttonCancel = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Cancel')
        buttonCancel.pack(side='left')