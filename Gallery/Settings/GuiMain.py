import tkinter

import cfg
from Utils.Styled import *

from .GuiGeneral import *

chosenMenu = 'General'


class Create(tkinter.Toplevel):
    def __init__(self):
        """Create tk TopLevel with tkinter.Labels and buttons. 
        Methods: just run class. 
        Imports: ManageDb from DataBase package."""

        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR)

        self.resizable(0,0)
        self.attributes('-topmost', 'true')
        self.title('Настройки')

        frameL = MyFrame(self)
        frameL.pack(side='left', padx=10, pady=10)

        frameR = MyFrame(self)
        frameR.pack(side='right', padx=10, pady=10)

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
        leftRightMenus = self.winfo_toplevel().winfo_children()
        leftMenu = leftRightMenus[0]
        rightMenu = leftRightMenus[1]

        leftBtns = leftMenu.winfo_children()
        gener = leftBtns[0]
        expert = leftBtns[1]

        general = rightMenu.winfo_children()[0]
        # general.pack_forget()


class General(MyFrame):
    def __init__(self, master):
        super().__init__(master)
        FullScan(self)


class BelowMenu(MyFrame):
    def __init__(self, master):
        super().__init__(master)

        buttonOk = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Ok')
        buttonOk.pack(side='left', padx=10)

        buttonCancel = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Cancel')
        buttonCancel.pack(side='left')
