import tkinter

root = tkinter.Tk()

class Btn(tkinter.Label):
    def __init__(self, master, bg="blue", **kwargs) -> None:
        super().__init__(master, kwargs, bg=bg)


bt = Btn(
    root,
    # bg="red",
    text="hello",
    width=10,
    height=10
    )
bt.pack()

root.mainloop()