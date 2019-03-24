from gi.repository import Gtk
from .confManager import ConfManager

class HydraPaperSettingsWindow(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/settings_window.glade'
        )
        self.box = self.builder.get_object('settingsBox')
        self.headerbar = self.builder.get_object('headerbar')

        self.set_titlebar(self.headerbar)
        self.add(self.box)

        self.builder.get_object('wallpaperSelectionModeToggle').set_active(
            self.confman.conf['selection_mode'] == 'double'
        )
        self.builder.get_object('keepFavoritesInMainviewToggle').set_active(
            self.confman.conf['favorites_in_mainview']
        )

        self.builder.connect_signals(self)

    def on_wallpaperSelectionModeToggle_state_set(self, toggle, state):
        self.confman.conf['selection_mode'] = 'double' if state else 'single'
        self.confman.save_conf()

    def on_keepFavoritesInMainviewToggle_state_set(self, toggle, state):
        self.confman.conf['favorites_in_mainview'] = state
        self.confman.save_conf()

    def on_resetFavoritesButton_clicked(self, btn):
        self.confman.conf['favorites'] = []
        self.confman.save_conf()
        # TODO: refresh both wallpaper view flowboxes
        # maybe do it by sending a signal?

    def on_clearCachesButton_clicked(self, btn):
        pass
