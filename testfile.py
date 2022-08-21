import tkinter
import cfg

class Lbutton(tkinter.Label):
    def __init__(self, master, cmd, txt):
        tkinter.Label.__init__(self, master)

        self.config(bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=17, height=2, text=txt)
        self.bind('<Button-1>', cmd)


root = tkinter.Tk()

frame = tkinter.Frame(root, bg='red', width=50, height=50)
frame.pack(side='left')

frame2 = tkinter.Frame(root, bg='blue', width=150, height=150)
frame2.pack(side='right')


b = Lbutton(frame2, lambda event: root.destroy(), 'hello')
b.pack()

root.mainloop()