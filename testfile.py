import os
import datetime
import cfg
# photo = '/Users/evlosh/Downloads/Py/photo/'
# dirr = []
# for root, dirs, files in os.walk(photo):
#     if '2019' in root or '2020' in root or '2021' in root:
#         dirr.append(root)
#         dirs[:] = []

def search_years():
    """
    Returns list dirs.
    Looking for folders with year names like "2018", "2020" etc.
    in `cfg.PHOTO_DIR`
    Looking for all folders in year named folders.
    """
    years = [str(y) for y in range(2018, datetime.datetime.now().year + 1)]
    y_dirs = []
    for root, dirs, _ in os.walk(cfg.config['PHOTO_DIR']):
        for d in dirs:
            [y_dirs.append(os.path.join(root, d)) if d in years else False]
    in_years = []
    for y_dir in y_dirs:
        for subdir in os.listdir(y_dir):
            new_dir = os.path.join(y_dir, subdir)
            [in_years.append(new_dir) if os.path.isdir(new_dir) else False]
    return in_years