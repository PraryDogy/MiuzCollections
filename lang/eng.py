class Eng:
    def __init__(self):
        # main
        self.ok = "Ok"
        self.cancel = "Cancel"
        self.all_colls = "All collections"
        self.close = "Close"

        # search_context
        self.search_paste = "Paste"
        self.search_clear = "Clear"

        # context menu
        self.preview = "Preview"
        self.info = "Info"
        self.show_finder = "Show in Finder"
        self.show_tiff = "Find tiff"

        # menu
        self.menu_title = "Menu"

        # settings
        self.settings_title = "Settings"
        self.settings_label = "Collections location"
        self.settings_browse = "Browse"
        self.settings_askexit = "Ask on exit"
        self.settings_reset = "Reset"
        self.settings_descr = (
            "If the collection name starts with _ or ."
            "\nMiuzCollections app will ignore it."
            )
        
        self.autoscan_time = "X"
        self.sett_autoscan = f"Update collections every {self.autoscan_time} mins"

        # status bar
        self.scaner_title = "Updating"
        self.upd_btn = "Update"

        # thumbnails
        self.thumbs_product = "Procuct"
        self.thumbs_models = "Models"
        self.thumbs_catalog = "Catalog"

        self.thumbs_alltime = "All time"
        self.thumbs_changed = "By date modified"
        self.thumbs_created = "By date created"
        self.thumbs_filter = "Filter"
        self.thumbs_sort = "Sort"
        self.thumbs_photo = "Photos"
        self.thumbs_filters = "Filters"
        self.thumbs_reset = "Reset date"
        self.thumbs_showmore = "Show more"
        self.thumbs_summary = "Total"
        self.thumbs_nophoto = "No photos"
        self.thumbs_withname = "with name"

        # filter window
        self.filter_title = "Filter"
        self.filter_start = "Start"
        self.filter_end = "End"
        self.filter_notselected = "Dates not selected"

        self.filter_product = "Product"
        self.filter_models = "Models"
        self.filter_catalog = "Catalog"

        self.filter_changed = "Date modified"
        self.filter_created = "Date created"
        self.filter_descr = (
            "Product - show procuct photos created by marketing department.",
            "Models - show model photos created by marketing department.",
            "Catalog - show photos for website.",
            "Sort - by date mofidied or date created.",
            )

        # custom date
        self.cust_title = "Enter the date"
        self.cust_l = "day.month.year"

        # ask exit
        self.askexit_exit = "Exit"

        # smb alert
        self.smb_title = "No connection."
        self.smb_descr = (
            '- Check internet connection.'
            '\n- Try to open any Miuz network folder.'
            '\n- Open settings and select collections folder.'
            '\n- Restart app.'

            '\nSupport: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        
        # info widget
        self.info_collection = "Collection "
        self.info_filename = "File name "
        self.info_chanded = "Date modified "
        self.info_resolution = "Resolution "
        self.info_size = "Size "
        self.info_path = "Path "

        # calendar
        self.calendar_days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

        # scaner
        self.scaner_prepare = "Preparing"

        # live text
        self.live_scan = "Scaning"
        self.live_from = "from"
        self.live_collections = "collections"
        self.live_added = "Added"
        self.live_newphoto = "new photos"
        self.live_finish = "Finishing"
        self.live_updating = "Updating"

        self.months_p = {
            1: "january",
            2: "february",
            3: "march",
            4: "april",
            5: "may",
            6: "june",
            7: "july",
            8: "august",
            9: "september",
            10: "october",
            11: "november",
            12: "december"}

        self.months = {
            k: v.capitalize()
            for k, v in self.months_p.items()
            }

    def update_autoscan(self):
        self.sett_autoscan = f"Update collections every {self.autoscan_time} mins"