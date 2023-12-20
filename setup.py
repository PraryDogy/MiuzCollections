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
from setup_ext import SetupExt

src = "icon.png"
img = icnsutil.IcnsFile()
img.add_media(file=src)
img.write(f"icon.icns")

APP = ["start.py"]

DATA_FILES = [cnf.db_name, cnf.thumb_err, "lang.json"]

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

SetupExt(py_ver="3.11", appname=cnf.app_name)
