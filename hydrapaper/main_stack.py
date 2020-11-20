from gettext import gettext as _
from gi.repository import Gtk
from .wallpapers_flowbox import HydraPaperWallpapersFlowbox


class HydraPapaerMainStack(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_style_context().add_class('view')

        self.main_flowbox = HydraPaperWallpapersFlowbox()
        self.favs_flowbox = HydraPaperWallpapersFlowbox(is_favorites=True)

        self.add_titled(
            self.main_flowbox, 'Wallpapers', _('Wallpapers')
        ).set_icon_name(
            'preferences-desktop-wallpaper-symbolic'
        )
        self.add_titled(
            self.favs_flowbox, 'Favorites', _('Favorites')
        ).set_icon_name(
            'emblem-favorite-symbolic'
        )
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
