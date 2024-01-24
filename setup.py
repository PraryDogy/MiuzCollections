# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

import shutil
import sys
import traceback
from datetime import datetime

import icnsutil
from setuptools import setup

from cfg import cnf
from setup_ext import SetupExt

src = "icon.png"
img = icnsutil.IcnsFile()
img.add_media(file=src)
img.write(f"icon.icns")

current_year = datetime.now().year

APP = ["start.py"]

DATA_FILES = [cnf.db_name, cnf.thumb_err, "lang/lang.json"]

OPTIONS = {"iconfile": "icon.icns",
           "plist": {"CFBundleName": cnf.app_name,
                     "CFBundleShortVersionString": cnf.app_ver,
                     "CFBundleVersion": cnf.app_ver,
                     "CFBundleIdentifier": f"com.evlosh.{cnf.app_name}",
                     "NSHumanReadableCopyright": (
                         f"Created by Evgeny Loshkarev"
                         f"\nCopyright © {current_year} MIUZ Diamonds."
                         f"\nAll rights reserved.")}}


if __name__ == "__main__":

    sys.argv.append("py2app")

    try:
        setup(
            app=APP,
            name=cnf.app_name,
            data_files=DATA_FILES,
            options={"py2app": OPTIONS},
            setup_requires=["py2app"],
        )
    except Exception:
        print(traceback.format_exc())
        shutil.rmtree("build")
        shutil.rmtree(".eggs")
        shutil.rmtree("dist")

    SetupExt(py_ver="3.11", appname=cnf.app_name)
