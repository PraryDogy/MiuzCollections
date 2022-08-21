import tkinter
import cfg

class MyButton(tkinter.Label):
    """Tkinter Label with binded function to 
    mouse left click and cfg styles."""

    def __init__(self, master, cmd, txt):

        tkinter.Label.__init__(self, master)

        self.config(bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=17, height=2, text=txt)
        self.bind('<Button-1>', cmd)


class MyFrame(tkinter.Frame):
    """Tkinter Frame with cfg styles"""
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        self.config(bg=cfg.BGCOLOR)


class MyLabel(tkinter.Label):
    """Tkinter Label with cfg styles"""
    def __init__(self, master):
        tkinter.Label.__init__(self, master)

        self.config(bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR)