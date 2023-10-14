import os
from cfg import cnf
import subprocess

zip_cmd = f"cd ~/Desktop && zip -r -X {cnf.app_name}.zip {cnf.app_name}.app"
subprocess.call(zip_cmd, shell=True)
