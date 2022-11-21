import os
import cfg
import shutil


for file in os.listdir(cfg.CFG_DIR)[1:]:
    if file.endswith('.db') and file != f'database {cfg.APP_VER}.db':
        os.remove(os.path.join(cfg.CFG_DIR, file))