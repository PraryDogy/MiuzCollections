import tkinter

from customtkinter import CTkProgressBar



root = tkinter.Tk()
root.geometry("300x100")
root.eval(f'tk::PlaceWindow {str(root)} center')


varr = tkinter.Variable(value=0)
progress = CTkProgressBar(master=root, width=200, variable=varr)
progress.pack(expand=1)

root.mainloop()