from gi.repository import Gtk
from .wnck_win_controller import change_minimize_state

class HydraPaperAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title('HydraPaper')

        self.headerbar_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/headerbar.glade'
        )
        self.headerbar = self.headerbar_builder.get_object('headerbar')
        self.menu_popover = self.headerbar_builder.get_object('menuPopover')
        self.wallpapers_folders_popover = self.headerbar_builder.get_object(
            'wallpapersFoldersPopover'
        )
        self.stack_switcher = self.headerbar_builder.get_object(
            'mainStackSwitcher'
        )

        self.headerbar_builder.connect_signals(self)

    def on_applyButton_clicked(self, btn):
        pass

    def on_menuBtn_clicked(self, btn):
        self.menu_popover.popup()

    def on_wallpapersFoldersBtn_clicked(self, btn):
        self.wallpapers_folders_popover.popup()

    def on_lowerAllOtherWindowsToggle_toggled(self, toggle):
        change_minimize_state(toggle)
