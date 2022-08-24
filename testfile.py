from smb.SMBConnection import SMBConnection
import subprocess
import cfg
import os


parent = os.path.dirname(__file__)
os.rmdir(os.path.join(parent, '.eggs'))