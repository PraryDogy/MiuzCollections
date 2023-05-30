class Rus:
    def __init__(self):
        # main
        self.ok = "Ок"
        self.cancel = "Отмена"
        self.all_colls = "Все коллекции"
        self.close = "Закрыть"

        # context menu
        self.preview = "Просмотр"
        self.info = "Инфо"
        self.show_finder = "Показать в Finder"
        self.show_tiff = "Показать tiff"

        # menu
        self.menu_title = "Меню"

        # settings
        self.settings_title = "Настройки"
        self.settings_label = "Расположение коллекций"
        self.settings_browse = "Обзор"
        self.settings_askexit = "Выход"
        self.settings_reset = "Сброс"
        self.settings_descr = (
            "Если имя коллекции начинается с _ или ."
            "\nпрограмма проигнорирует ее."
            "\nДоступные языки: русский, английский."
            "\nВыход - спрашивать при выходе."
            )
        
        # status bar
        self.scaner_title = "Обновление"
        self.upd_btn = "Обновить"

        # thumbnails
        self.thumbs_marketing = "Только имиджи"
        self.thumbs_catalog = "Только каталог"
        self.thumbs_showall = "Все фото"
        self.thumbs_alltime = "За все время"
        self.thumbs_changed = "По дате изменения"
        self.thumbs_created = "По дате создания"
        self.thumbs_summary = "Всего"
        self.thumbs_filter = "Фильтр"
        self.thumbs_sort = "Сортировка"
        self.thumbs_photo = "Фото"
        self.thumbs_filters = "Фильтры"
        self.thumbs_reset = "Сбросить даты"
        self.thumbs_showmore = "Позазать еще"

        # filter window
        self.filter_title = "Фильтр"
        self.filter_start = "Начало"
        self.filter_end = "Конец"
        self.filter_oneday = "За один день"
        self.filter_marketing = "Имиджи"
        self.filter_catalog = "Каталог"
        self.filter_showall = "Показать все"
        self.filter_changed = "Дата изменения"
        self.filter_created = "Дата создания"
        self.filter_descr = (
            "Имиджи - показывать только рекламные фото.",
            "Каталог - показывать только каталожные фото.",
            "Сортировка - по дате изменения или по дате создания.",
            )
        
        # ask exit
        self.askexit_exit = "Выйти"

        # smb alert
        self.smb_title = "Нет подключения."
        self.smb_descr = (
            '\n- Проверьте подключение к интернету.'
            '\n- Откройте любую папку на сетевом диске,'
            '\n- Укажите правильный путь к коллекциям в настройках'
            '\n- Перезапустите приложение.'

            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        
        # info widget
        self.info_collection = "Коллеция "
        self.info_filename = "Имя файла "
        self.info_chanded = "Дата изменения "
        self.info_resolution = "Разрешение "
        self.info_size = "Размер "
        self.info_path = "Расположение "

        # calendar
        self.calendar_days = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

        # scaner
        self.scaner_prepare = "Подготовка"

        # live text
        self.live_scan = "Сканирую"
        self.live_from = "из"
        self.live_collections = "коллекций"
        self.live_added = "Добавлено"
        self.live_newphoto = "новых фото"
        self.live_finish = "Завершаю"
        self.live_updating = "Обновление"

        self.months_parental = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"}

        self.months = {
            1: "Январь",
            2: "Февраль",
            3: "Март",
            4: "Апрель",
            5: "Май",
            6: "Июнь",
            7: "Июль",
            8: "Август",
            9: "Сентябрь",
            10: "Октябрь",
            11: "Ноябрь",
            12: "Декабрь"}