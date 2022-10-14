"""
Stores text for settings module.

* var descriptions: list with stored text variables
"""

import cfg


PHOTO_DIR = (
    'Путь к папке со всеми фото.'
    )

COLL_FOLDERS = (
    'Путь к папке с коллекциями.'
    )

RT_FOLDER = (
    'Имя папки с ретушью. Подразумевается, что внутри папки с этим именем'
    'будут отретушированные фото.'
    )

FILE_AGE = (
    'По умолчанию программа ищет отретушированные фотографии за последние '
    f'{cfg.FILE_AGE} дней. Можно указать другое количество дней. Чем больше'
    'дней, тем дольше сканирование. Можно так же воспользоваться полным '
    'сканированием за все время в основных настройках.'
    )

descriptions = {
    'PHOTO_DIR': PHOTO_DIR,
    'COLL_FOLDERS': COLL_FOLDERS,
    'RT_FOLDER': RT_FOLDER,
    'FILE_AGE': FILE_AGE
    }