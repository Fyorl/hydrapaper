from gi.repository import Gtk, Handy
from .wallpapers_folders_view import HydraPaperWallpapersFoldersView
from .confManager import ConfManager


class HydraPaperHeaderbar(Handy.HeaderBar):
    def __init__(self, window, apply_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confman = ConfManager()
        self.apply_handler = apply_handler
        self.set_show_title_buttons(True)
        self.stack_switcher = Handy.ViewSwitcher()
        self.squeezer = Handy.Squeezer()
        self.nobox = Gtk.Label()
        self.bottom_bar = window.bottom_bar
        self.squeezer.add(self.stack_switcher)
        self.squeezer.add(self.nobox)
        self.squeezer.connect('notify::visible-child', self.on_squeeze)
        self.set_title_widget(self.squeezer)

        self.folders_view = HydraPaperWallpapersFoldersView(window)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/headerbar.ui'
        )
        self.wallpapers_folders_popover = self.builder.get_object(
            'wallpapersFoldersPopover'
        )
        self.wallpapers_folders_popover.set_child(self.folders_view)
        self.menu_popover = self.builder.get_object('menuPopover')
        self.apply_button = self.builder.get_object('applyButton')
        self.apply_button.connect('clicked', self.on_applyButton_clicked)
        self.menu_button = self.builder.get_object('menuBtn')
        self.wallpapers_folders_button = self.builder.get_object(
            'wallpapersFoldersBtn'
        )
        left_widgets = [self.wallpapers_folders_button]
        right_widgets = [self.menu_button, self.apply_button]
        for w in left_widgets:
            self.pack_start(w)
        for w in right_widgets:
            self.pack_end(w)

        self.ww_popover = Gtk.Popover()
        self.ww_popover_content_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/which_wallpaper_box.ui'
        )
        self.ww_container = self.ww_popover_content_builder.get_object(
            'ww_container'
        )
        self.ww_popover_content_builder.get_object(
            'desktop_btn'
        ).connect('clicked', self.on_desktop_clicked)
        self.ww_popover_content_builder.get_object(
            'lockscreen_btn'
        ).connect('clicked', self.on_lockscreen_clicked)
        self.ww_popover_content_builder.get_object(
            'both_btn'
        ).connect('clicked', self.on_both_clicked)
        self.ww_popover.set_child(self.ww_container)
        self.ww_popover.set_autohide(True)
        self.ww_popover.set_parent(self.apply_button)

    def on_squeeze(self, *args):
        self.bottom_bar.set_reveal(
            self.squeezer.get_visible_child() == self.nobox
        )

    def on_applyButton_clicked(self, btn):
        if self.confman.has_lockscreen_wallpaper:
            self.ww_popover.popup()
        else:
            self.apply_handler(self.apply_button, lockscreen=False)

    def on_desktop_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=False)

    def on_lockscreen_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=True)

    def on_both_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=False)
        self.apply_handler(self.apply_button, lockscreen=True)
