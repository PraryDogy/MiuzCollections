# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

import os
import shutil

from setuptools import setup
import cfg



APP = ['start.py']
DATA_FILES = [
    os.path.join(os.path.dirname(__file__), 'gui', 'upd.png'),
    os.path.join(os.path.dirname(__file__), 'gui', 'logo.png'),
    ]

OPTIONS = {
    'iconfile': 'icon.icns',
    'plist': {
    'CFBundleName': cfg.APP_NAME,
    'CFBundleShortVersionString':cfg.APP_VER,
    'CFBundleVersion': cfg.APP_VER,
    'CFBundleIdentifier':f'com.evlosh.{cfg.APP_NAME}',
    'NSHumanReadableCopyright': (
        'Created by Evgeny Loshkarev'
        '\nCopyright © 2022 MIUZ Diamonds. All rights reserved.')
    }
    }

setup(
    app=APP,
    name=cfg.APP_NAME,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'opencv-python',
        'Pillow',
        'SQLAlchemy',
        ]
    )


parent = os.path.dirname(__file__)
LIB = '/Users/Loshkarev/Documents/Разное/Projects/files/lib'
pasteHere = os.path.join(os.path.dirname(__file__), 'dist',
                        f'{cfg.APP_NAME}.app', 'Contents', 'lib')

shutil.copytree(LIB, pasteHere)

file = os.path.join(parent, 'dist', f'{cfg.APP_NAME}.app')
desktop = os.path.join(
    os.path.join(os.path.expanduser('~')), 'Desktop', f'{cfg.APP_NAME}.app')
shutil.move(file, desktop)

shutil.rmtree(os.path.join(parent, 'build'))
shutil.rmtree(os.path.join(parent, '.eggs'))
shutil.rmtree(os.path.join(parent, 'dist'))
