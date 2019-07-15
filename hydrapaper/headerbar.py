from gi.repository import Gtk, Handy
from .wnck_win_controller import change_minimize_state
from .wallpapers_folders_view import HydraPaperWallpapersFoldersView

class HydraPaperHeaderbar(Handy.HeaderBar):
    def __init__(self, window, apply_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_handler = apply_handler
        self.set_show_close_button(True)
        self.stack_switcher = Handy.ViewSwitcher()
        self.set_custom_title(self.stack_switcher)

        self.folders_view = HydraPaperWallpapersFoldersView(window)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/headerbar.glade'
        )
        self.wallpapers_folders_popover = self.builder.get_object(
            'wallpapersFoldersPopover'
        )
        self.wallpapers_folders_popover.add(self.folders_view)
        self.menu_popover = self.builder.get_object('menuPopover')
        self.apply_spinner = self.builder.get_object('applySpinner')
        self.apply_button = self.builder.get_object('applyButton')
        self.lower_windows_toggle = self.builder.get_object(
            'lowerAllOtherWindowsToggle'
        )
        self.menu_button = self.builder.get_object('menuBtn')
        self.wallpapers_folders_button = self.builder.get_object(
            'wallpapersFoldersBtn'
        )
        left_widgets = [
            self.wallpapers_folders_button,
            self.lower_windows_toggle
        ]
        right_widgets = [
            self.apply_button,
            self.menu_button,
            self.apply_spinner
        ]

        for w in left_widgets:
            self.pack_start(w)
        for w in right_widgets:
            self.pack_end(w)
        self.builder.connect_signals(self)

    def on_menuBtn_clicked(self, btn):
        self.menu_popover.popup()

    def on_wallpapersFoldersBtn_clicked(self, btn):
        self.wallpapers_folders_popover.popup()

    def on_lowerAllOtherWindowsToggle_toggled(self, toggle):
        change_minimize_state(toggle = toggle)

    def on_applyButton_clicked(self, btn):
        self.apply_handler(btn)
