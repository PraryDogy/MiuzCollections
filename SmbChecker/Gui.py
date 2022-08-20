import subprocess
import tkinter

import cfg
    

def Create():
    newWin = tkinter.Toplevel(cfg.ROOT)
    newWin.attributes('-topmost', 'true')
    newWin.resizable(0,0)

    newWin.title('Нет подключения')
    newWin.config(bg=cfg.BGCOLOR, padx=10, pady=10)
    
    txt = (
        'Нет подключения к сетевому диску Miuz.'
        '\nПрограмма работает в офлайн режиме.'
        '\nНажмите "Подключиться" или'
        '\nоткройте любую папку на сетевом диске.'
        '\n\nПоддержка: loshkarev@miuz.ru'
        '\nTelegram: evlosh'
        '\n'
        )

    descrLbl = tkinter.Label(
        newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
        text=txt, justify='center', pady=10)
    descrLbl.pack(fill="x")

    btns = tkinter.Frame(newWin, bg=cfg.BGCOLOR)
    btns.pack(anchor='center')


    def Connect(curBtn):
        curBtn.config(bg=cfg.BGPRESSED)
        p = subprocess.Popen(f'open {cfg.SMB_CONN}'.split(' '))
        p.communicate()
        cfg.ROOT.after(1000, lambda: curBtn.config(bg=cfg.BGBUTTON))


    connBtn = tkinter.Label(
        btns, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
        text='Подключиться', width=17, height=2)
    connBtn.pack(side='left')
    connBtn.bind('<Button-1>', lambda event: Connect(connBtn))

    betwBtns = tkinter.Frame(btns, bg=cfg.BGCOLOR, width=15)
    betwBtns.pack(side='left')

    clsBtn = tkinter.Label(btns, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
        text='Закрыть', width=17, height=2)
    clsBtn.bind('<Button-1>', lambda event: newWin.destroy())
    clsBtn.pack(side='left')

    cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')