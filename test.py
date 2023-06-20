import tkinter


root = tkinter.Tk()

def test():
    pass


a = root.after(1000, test)

print(type(a))