import tkinter
import cfg

class MyButton(tkinter.Label):
    """Tkinter Label with binded function to 
    mouse left click and cfg styles.
    Methods: Cmd"""

    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=17, height=2)

    def Cmd(self, cmd):
        """Bind tkinter label to left click"""
        self.bind('<Button-1>', cmd)

    def Press(self):
        self.configure(bg=cfg.BGPRESSED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BGBUTTON))
        

class MyFrame(tkinter.Frame):
    """Tkinter Frame with cfg styles"""
    def __init__(self, master, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR)


class MyLabel(tkinter.Label):
    """Tkinter Label with cfg styles"""
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR)


class Scrollable:
    def Scrollable(self, imgFrame):
        '''
        Returns tkinter scrollable frame. 
        Pack inside this frame any content.
        '''
        
        container = tkinter.Frame(imgFrame)

        canvas = tkinter.Canvas(
            container, bg=cfg.BGCOLOR, highlightbackground=cfg.BGCOLOR)

        scrollbar = tkinter.Scrollbar(
            container, width=12, orient='vertical', command=canvas.yview)

        self.scrollable = tkinter.Frame(canvas)

        self.scrollable.bind(
            "<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta), "units"),
            # lambda e: canvas.yview_scroll(-1*(e.delta/120), "units")
            )

        canvas.create_window((0,0), window=self.scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill=tkinter.BOTH, expand=True)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        return self.scrollable
