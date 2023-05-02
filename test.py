from tkinter import *
import sys

if __name__ == '__main__':
       root = Tk()
       root.configure(bg="black")
       hero_text = Label(root, fg='white', bg='black', text='HERO TEXT')
       hero_text.grid(row=0, sticky=N+W)
       print(root.tk.exprstring('$tcl_library'))
       print(root.tk.exprstring('$tk_library'))

       print(sys.version_info)