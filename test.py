import os
import cfg

def get_coll_name(src: str):
    coll = src.replace(cfg.config["COLL_FOLDER"], "")
    coll = coll.strip(os.sep)
    return coll.split(os.sep)[0]