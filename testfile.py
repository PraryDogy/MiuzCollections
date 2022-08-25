import os
import tkinter
import shutil
import cfg


lib = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    'files', 
    'lib'
    )


print(os.path.exists(lib))