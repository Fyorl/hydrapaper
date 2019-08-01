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
        ]
        for w in left_widgets:
            self.pack_start(w)
        for w in right_widgets:
            self.pack_end(w)

        self.ww_popover = Gtk.Popover()
        self.ww_popover_content_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/which_wallpaper_box.glade'
        )
        self.ww_container = self.ww_popover_content_builder.get_object(
            'ww_container'
        )
        # self.set_desktop_btn = self.ww_popover_content_builder.get_object(
        #     'desktop_btn'
        # )
        # self.set_lockscreen_btn = self.ww_popover_content_builder.get_object(
        #     'lockscreen_btn'
        # )
        # self.set_both_btn = self.ww_popover_content_builder.get_object(
        #     'both_btn'
        # )
        self.ww_popover_content_builder.connect_signals(self)
        self.ww_popover.add(self.ww_container)
        self.ww_popover.set_modal(True)
        self.ww_popover.set_relative_to(self.apply_button)


        self.builder.connect_signals(self)

    def on_menuBtn_clicked(self, btn):
        self.menu_popover.popup()

    def on_wallpapersFoldersBtn_clicked(self, btn):
        self.wallpapers_folders_popover.popup()

    def on_lowerAllOtherWindowsToggle_toggled(self, toggle):
        change_minimize_state(toggle = toggle)

    def on_applyButton_clicked(self, btn):
        self.ww_popover.popup()
        # self.apply_handler(btn)

    def on_desktop_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen = False)

    def on_lockscreen_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen = True)

    def on_both_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen = False)
        self.apply_handler(self.apply_button, lockscreen = True)
