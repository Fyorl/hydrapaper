from gi.repository import Gtk
from .wallpapers_flowbox import HydraPaperWallpapersFlowbox

class HydraPapaerMainStack(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_flowbox = HydraPaperWallpapersFlowbox()
        self.favs_flowbox = HydraPaperWallpapersFlowbox(is_favorites = True)

        self.add_named(self.main_flowbox, 'Wallpapers')
        self.add_named(self.favs_flowbox, 'Favorites')
