"""
Stores text for settings module.

* var descriptions: list with stored text variables
"""

PHOTO_DIR = (
    'Настройки применятся после перезапуска.'
    '\n\nГалерея фото.'
    '\nПуть к папке с фото, внутри которой находятся папки,'
    '\nназванные по годам (2019, 2021, 2022 и т.п.).'
    '\nНапример: /Путь/к/фото/AllPhotos'

    '\n\nПрограмма будет сканировать содержимое только'
    '\nв папках, названных по годам.'
    '\nСканирует: /Путь/к/фото/AllPhotos/2022'
    '\nНе сканирует: /Путь/к/фото/AllPhotos/Новая папка'

    '\n\nЕсли внутри галереи фото не будет папок'
    '\nс годами, программа ничего не найдет.'
    '\nЭто обусловлено тем, чтобы не тратить время'
    '\nна сканирование большого объема данных.'
    )

COLL_FOLDER = (
    'Имя папки с коллекциями.'
    '\nПодразумевается, что внутри папки с таким'
    '\nименем будут папки с коллекциями.'
    '\nПрограмма будет искать эту папку внутри'
    '\nпапок, названных по годам. Например:'
    '\n/Путь/к/фото/AllPhotos/2022/_Collections'

    '\n\nЕсли в каждой папке, названной по году, есть'
    '\nпапка с коллекциями, программа отобразит их,'
    '\nно должно быть одинаковое имя папки коллекций.'
    )

RT_FOLDER = (
    'Имя папки с ретушью.'
    '\nПодразумевается, что внутри папки с таким'
    '\именем будут отретушированные фото.'
    '\nПрограмма будет искать такую папку внутри папок,'
    '\nназванных по годам. Например:'
    '\n/Путь/к/фото/AllPhotos/2022/Август/Smm/Retouch'

    '\n\nКоличество папок с таким именем неограничено.'
    )

FILE_AGE = (
    'По умолчанию программа ищет папки с ретушью'
    '\nв галерее фото за последние 60 дней.'
    '\nМожно указать другое количество дней.'
    '\nЧем больше число, тем дольше сканирование.'
    '\nМожно так же воспользоваться полным сканированием'
    '\nза все время в основных настройках.'
    )


descriptions = [PHOTO_DIR, COLL_FOLDER, RT_FOLDER, FILE_AGE]