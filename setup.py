# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

import os
import shutil

from setuptools import setup
from cfg import conf
import icnsutil


packages = [
    'cffi',
        'colour',
        'greenlet',
        'icnsutil',
        'importlib-metadata',
        'numpy',
        'opencv-python',
        'Pillow',
        'pycparser',
        'SQLAlchemy',
        'tkmacosx',
        'typing-extensions',
        'zipp',
        ]

src = 'icon.png'
img = icnsutil.IcnsFile()
img.add_media(file=src)
img.write(f'icon.icns')

APP = ['start.py']

DATA_FILES = [
    conf.db_name, conf.thumb_err
    ]

OPTIONS = {
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': conf.app_name,
        'CFBundleShortVersionString': conf.app_ver,
        'CFBundleVersion': conf.app_ver,
        'CFBundleIdentifier':f'com.evlosh.{conf.app_name}',
        'NSHumanReadableCopyright': (
            'Created by Evgeny Loshkarev'
            '\nCopyright © 2023 MIUZ Diamonds.'
            '\nAll rights reserved.'
            )
            }
            }

setup(
    app = APP,
    name = conf.app_name,
    data_files = DATA_FILES,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app'],
    install_requires = []
    )

shutil.copytree(
    "lib",
    f"dist/{conf.app_name}.app/Contents/lib"
    )

shutil.move(
    f"dist/{conf.app_name}.app",
    os.path.expanduser(f"~/Desktop/{conf.app_name}.app")
    )

shutil.rmtree('build')
shutil.rmtree('.eggs')
shutil.rmtree('dist')
