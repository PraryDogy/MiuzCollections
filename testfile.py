import tkinter
import asyncio
import time

root = tkinter.Tk()
lbl = tkinter.Label(root, text='1', width=10, height=5)
lbl.pack()

async def count():
    for i in range(0, 10):
        lbl['text'] = i
        await asyncio.sleep(2)


async def scaner():
    print('start scan')
    await count()
    print('end scan')

def start():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(count())


btn = tkinter.Button(root, command=start, text='start')
btn.pack()
root.eval(f'tk::PlaceWindow {root} center')


root.mainloop()