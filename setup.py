# -*- coding: utf-8 -*-

"""
    python setup.py py2app
"""

from setuptools import setup
from cfg import APP_VER
import os

APP = ['start.py']
DATA_FILES = [os.path.join(
    os.path.dirname(__file__), 
    'Gallery/Settings/upd.jpg')
              ]
OPTIONS = {
    'iconfile': 'icon.icns',
    'plist': {
    'CFBundleName': 'MiuzGallery',
    'CFBundleShortVersionString':APP_VER, 
    'CFBundleVersion': APP_VER, 
    'CFBundleIdentifier':'com.evlosh.MiuzGallery', 
    'NSHumanReadableCopyright': 'Created by Evgeny Loshkarev\nCopyright © 2022 MIUZ Diamonds. All rights reserved.'
    }
    }

setup(
    app=APP,
    name='MiuzGallery',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'opencv-python', 
        'Pillow', 
        'SQLAlchemy', 
        'yadisk'
        ]
    )

