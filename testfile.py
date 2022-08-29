import tkinter

from Utils.Styled import MyButton

root = tkinter.Tk()


class Buttons(MyButton):
    def __init__(self, master):
        
        for i in range(0, 15):
            MyButton.__init__(self, master, text=i)
            kk = self['text']
            self.Cmd(lambda e, n=kk: print(n))

            self.pack(pady=(0, 10))

Buttons(root)
root.mainloop()