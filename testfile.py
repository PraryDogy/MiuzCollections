from tkinter import *

def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets
    '''

    try:
        def rClick_Copy(e: Event, apnd=0):
            e.widget.event_generate('<Command-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Command-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Command-v>')

        e.widget.focus()

        nclst=[
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e)),
               ]

        rmenu = Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except TclError:
        print (' - rClick menu, something wrong')
        pass

    return "break"


def rClickbinder(r):

    try:
        for b in [ 'Text', 'Entry', 'Listbox', 'Label']: #
            r.bind_class(b, sequence='<Button-3>',
                         func=rClicker, add='')
    except TclError:
        print (' - rClickbinder, something wrong')
        pass


if __name__ == '__main__':
    master = Tk()
    ent = Entry(master, width=50)
    ent.pack(anchor="w")

    #bind context menu to a specific element
    ent.bind('<Button-2>',rClicker, add='')
    #or bind it to any Text/Entry/Listbox/Label element
    #rClickbinder(master)

    master.mainloop()
