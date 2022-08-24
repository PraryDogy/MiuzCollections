import os

import cfg


def Check():
    '''
    \ncheck smb path
    \nreturn bool
    '''
    if not os.path.exists(cfg.PHOTO_DIR):
        return False
    return True
