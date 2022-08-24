from smb.SMBConnection import SMBConnection
import subprocess
import cfg
import os


thumbs = [1, 2]
colls = 5

if len(thumbs) < colls:
    for i in range(0, colls-len(thumbs)):
        print(i)