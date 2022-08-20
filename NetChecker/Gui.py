import tkinter

import cfg


def Create():
    newWin = tkinter.Toplevel()
    
    newWin.title('Нет подключения')
    newWin.config(bg=cfg.BGCOLOR, padx=10, pady=10)
    newWin.resizable(0, 0)
    
    txt = (
            'Нет подключения к интернету.'
            '\nПодключение необходимо'
            '\nдля просмотра фото на сетевом диске.'
            )

    descrLabel = tkinter.Label(
        newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text=txt)
    descrLabel.pack()

    aboveBtn = tkinter.Frame(
        newWin, bg=cfg.BGCOLOR, height=10)
    aboveBtn.pack()
    
    closeBtn = tkinter.Label(
        newWin, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
        height=2, width=17, text='Закрыть')
    closeBtn.pack()
    closeBtn.bind('<Button-1>', lambda event: cfg.ROOT.destroy())

    cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')
