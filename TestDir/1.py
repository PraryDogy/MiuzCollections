from tkinter import *   # Python 3

def new_file():
    # ...
    pass

def about_dialog():
    root.tk.call('tk::mac::standardAboutPanel')

root = Tk()
win = Toplevel(root)
menubar = Menu(win)
menu_file = Menu(menubar)
# ...
menubar.add_cascade(menu=menu_file, label='File')
# ...
menu_file.add_command(label='New', command=new_file)
# ...
root.createcommand('tkAboutDialog', about_dialog)
win['menu'] = menubar
root.mainloop()