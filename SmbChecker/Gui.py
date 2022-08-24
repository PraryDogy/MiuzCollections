import json
import os
import subprocess
import tkinter

import cfg


def Create():
    newWin = tkinter.Toplevel(cfg.ROOT)
    newWin.attributes('-topmost', 'true')
    newWin.resizable(0,0)

    newWin.title('Нет подключения')
    newWin.configure(bg=cfg.BGCOLOR, padx=10, pady=10)
    
    txt = (
        'Нет подключения к сетевому диску Miuz. '
        'Программа работает в офлайн режиме. '
        '- Откройте настройки > эксперт, и введите правильный адрес '
        'и нажмите "Подключиться". '
        '- Проверьте подключение к интернету. '
        '- Откройте любую папку на сетевом диске, введите логин и пароль'
        'если потребуется'       
        'Поддержка: loshkarev@miuz.ru'
        'Telegram: evlosh'
        )

    descrLbl = tkinter.Label(
        newWin, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
        text=txt, justify='center', pady=10, wraplength=350)
    descrLbl.pack(fill="x", padx=15)

    btns = tkinter.Frame(newWin, bg=cfg.BGCOLOR)
    btns.pack(anchor='center')


    def Connect():
        
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)
        SMB_CONN = data['SMB_CONN']
        os.system(f"osascript -e 'mount volume \"{SMB_CONN}\"'")
        
        if not os.path.exists(cfg.PHOTO_DIR):
            return
        
        else:
            newWin.destroy()
            
        # p = subprocess.Popen(f'open {cfg.SMB_CONN}'.split(' '))
        # p.communicate()
        

    connBtn = tkinter.Label(
        btns, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
        text='Подключиться', width=17, height=2)
    connBtn.pack(side='left')
    connBtn.bind('<Button-1>', lambda event: Connect())

    betwBtns = tkinter.Frame(btns, bg=cfg.BGCOLOR, width=15)
    betwBtns.pack(side='left')

    clsBtn = tkinter.Label(btns, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
        text='Закрыть', width=17, height=2)
    clsBtn.bind('<Button-1>', lambda event: newWin.destroy())
    clsBtn.pack(side='left')

    cfg.ROOT.eval(f'tk::PlaceWindow {newWin} center')
