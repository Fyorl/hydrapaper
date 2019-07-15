from gettext import gettext as _
from gi.repository import Gtk
from .wallpapers_flowbox import HydraPaperWallpapersFlowbox

class HydraPapaerMainStack(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_flowbox = HydraPaperWallpapersFlowbox()
        self.favs_flowbox = HydraPaperWallpapersFlowbox(is_favorites = True)

        self.add_titled(self.main_flowbox, 'Wallpapers', _('Wallpapers'))
        self.add_titled(self.favs_flowbox, 'Favorites', _('Favorites'))
        self.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
