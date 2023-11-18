# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

import os
import shutil
import subprocess

import icnsutil
from setuptools import setup

from cfg import cnf

src = "icon.png"
img = icnsutil.IcnsFile()
img.add_media(file=src)
img.write(f"icon.icns")

APP = ["start.py"]

DATA_FILES = [cnf.db_name, cnf.thumb_err]

OPTIONS = {"iconfile": "icon.icns",
           "plist": {"CFBundleName": cnf.app_name,
                     "CFBundleShortVersionString": cnf.app_ver,
                     "CFBundleVersion": cnf.app_ver,
                     "CFBundleIdentifier":f"com.evlosh.{cnf.app_name}",
                     "NSHumanReadableCopyright": (
                         "Created by Evgeny Loshkarev"
                         "\nCopyright © 2023 MIUZ Diamonds."
                         "\nAll rights reserved.")}}

setup(
    app = APP,
    name = cnf.app_name,
    data_files = DATA_FILES,
    options = {"py2app": OPTIONS},
    setup_requires = ["py2app"],
    install_requires = []
    )

ver = "3.11"
lib_src = f"/Library/Frameworks/Python.framework/Versions/{ver}/lib"
folders = "tcl8", "tcl8.6", "tk8.6"

for i in folders:
    shutil.copytree(
        os.path.join(lib_src, i),
        os.path.join(f"dist/{cnf.app_name}.app/Contents/lib", i)
        )

folder = os.path.join(os.path.expanduser("~/Desktop"), cnf.app_name)

if not os.path.exists(folder):
    os.mkdir(folder)
else:
    shutil.rmtree(folder)
    os.mkdir(folder)

subprocess.Popen(
    ["ln", "-s", "/Applications", os.path.join(folder, "Программы")]
        )
shutil.move(f"dist/{cnf.app_name}.app", f"{folder}/{cnf.app_name}.app")


shutil.rmtree("build")
shutil.rmtree(".eggs")
shutil.rmtree("dist")

subprocess.Popen(["open", "-R", folder])