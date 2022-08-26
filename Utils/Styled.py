import tkinter
import cfg

class MyButton(tkinter.Label):
    """Tkinter Label with binded function to 
    mouse left click and cfg styles.
    Methods: Cmd"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=17, height=2)

    def Cmd(self, cmd):
        """Bind tkinter label to left click"""
        self.bind('<Button-1>', cmd)


class MyFrame(tkinter.Frame):
    """Tkinter Frame with cfg styles"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=cfg.BGCOLOR)


class MyLabel(tkinter.Label):
    """Tkinter Label with cfg styles"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR)