import tkinter

import cfg


def Create():
    '''
    return tkinter TopLevel
    '''
    
    newWin = tkinter.Toplevel()
    newWin.title('Подождите')
    newWin.configure(bg=cfg.BGCOLOR, padx=5, pady=10)
    newWin.resizable(0,0)

    descr = tkinter.Label(
        newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
        pady=10, text='Скачиваю дополнения.')
    descr.pack()

    cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')
     
    return newWin
