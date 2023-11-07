class Eng:
    def __init__(self):
        self.name = "en"

        self.language = "English"
        self.lang_label = "Language/Язык"
        self.up = "Up"
        self.ok = "Ok"
        self.cancel = "Cancel"
        self.all_colls = "All collections"
        self.close = "Close"
        self.paste = "Paste"
        self.clear = "Clear"
        self.search = "Search"
        self.view = "View"
        self.info = "Info"
        self.menu = "Menu"
        self.settings = "Settings"
        self.browse = "Browse"
        self.exit = "Exit"
        self.reset = "Reset"
        self.mins = "mins."
        self.product = "Product"
        self.models = "Models"
        self.catalog = "Catalog"
        self.updating = "Updating"
        self.update = "Update"
        self.filter = "Filter"
        self.filters = "Filters"
        self.sort = "Sort"
        self.photo = "Photo"
        self.total = "Total"
        self.start = "Start"
        self.end = "End"
        self.go_out = "Go out"
        self.preparing = "Preparing"
        self.scaning = "Scaning"
        self.copying = "Copying"
        self.from_pretext = "from"
        self.added = "Added"
        self.finishing = "Finishing"
        self.copy = "Copy"
        self.resolution = "Resolution"
        self.file_size = "Size"
        self.file_path = "Location"
        self.collection = "Collection"
        self.dates = "Dates"

        self.sett_descr = (
            "If the collection name starts with _ or ."
            "\nMiuzCollections app will ignore it."
            )

        self.filter_descr = (
            "Product - show procuct photos created by marketing department.",
            "Models - show model photos created by marketing department.",
            "Catalog - show photos for website.",
            "Sort - by date mofidied or date created.",
            )

        self.smb_descr = (
            "- Check internet connection."
            "\n- Try to open any Miuz network folder."
            "\n- Open settings and select collections folder."
            "\n- Restart app."

            "\nSupport: loshkarev@miuz.ru"
            "\nTelegram: evlosh"
            )

        self.lang_descr = "Press ok to change language"


        self.please_wait = "Please, wait"
        self.no_tiff = "Can't find tiff"
        self.no_jpg = "Can't find jpg"
        self.to_downloads = "to downloads"
        self.copy_all = "Copy all"
        self.find_jpg = "Find jpg"
        self.find_tiff = "Find tiff"
        self.copy_path_tiff = "Copy tiff location"
        self.copy_path_jpg = "Copy jpg location"
        self.reveal_coll = "Reveal collection"
        self.colls_path = "Collections location"
        self.down_path = "Downloads folder"
        self.scan_time = "x"
        self.update_every = f"Update collections every"
        self.show_more = "Show more"
        self.no_photo = "No photos"
        self.with_name = "with name"
        self.for_all_time = "For all time"
        self.date_changed_by = "By date changed"
        self.date_created_by = "By date created"
        self.date_changed = "Date changed"
        self.date_created = "Date created"
        self.reset_dates = "Dates reset"
        self.dates_not_sel = "No dates selected"
        self.enter_date = "Enter date"
        self.d_m_y = "day.month.year"
        self.no_connection = "No connection"
        self.file_name = "Filename"
        self.remove_fromapp = "Remove from app"
        self.fullsize = "Download fullsize jpg"
        self.group_fullsize = "Download fullsize jpg"
        self.show_all = "Show all"
        self.reset_search = "Reset search"

        self.colls_case = "collections"
        self.new_photo_case = "new_photos"


        self.calendar_days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        self.months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"}

        self.months_case = {
            k: v.lower()
            for k, v in self.months.items()
            }
