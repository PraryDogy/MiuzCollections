import os
import subprocess

filename = "IMG_4069"

names = []

for root, dirs, files in os.walk("/Volumes/Untitled/_Collections/9 Liola/"):
    for file in files:
        if file.endswith((".psd", ".PSD", ".tiff", ".TIFF")):
            if filename in file:
                subprocess.call(["open", "-R", root + file])