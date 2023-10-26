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

packages = [
    "cffi",
        "colour",
        "greenlet",
        "icnsutil",
        "importlib-metadata",
        "numpy",
        "opencv-python",
        "Pillow",
        "pycparser",
        "SQLAlchemy",
        "tkmacosx",
        "typing-extensions",
        "zipp",
        ]

src = "icon.png"
img = icnsutil.IcnsFile()
img.add_media(file=src)
img.write(f"icon.icns")

APP = ["start.py"]

DATA_FILES = [
    cnf.db_name, cnf.thumb_err
    ]

OPTIONS = {
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleName": cnf.app_name,
        "CFBundleShortVersionString": cnf.app_ver,
        "CFBundleVersion": cnf.app_ver,
        "CFBundleIdentifier":f"com.evlosh.{cnf.app_name}",
        "NSHumanReadableCopyright": (
            "Created by Evgeny Loshkarev"
            "\nCopyright © 2023 MIUZ Diamonds."
            "\nAll rights reserved."
            )
            }
            }

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

dest = os.path.expanduser(f"~/Desktop/{cnf.app_name}.app")

shutil.move(f"dist/{cnf.app_name}.app", dest)

shutil.rmtree("build")
shutil.rmtree(".eggs")
shutil.rmtree("dist")

zip_cmd = f"cd ~/Desktop && zip -r -X {cnf.app_name}.zip {cnf.app_name}.app"
subprocess.call(zip_cmd, shell=True)

subprocess.Popen(["open", "-R", dest])