from gettext import gettext as _
from gi.repository import Adw
from .wallpapers_flowbox import HydraPaperWallpapersFlowbox


class HydraPapaerMainStack(Adw.ViewStack):
    def __init__(self):
        super().__init__(
            vexpand=True, hexpand=True
        )

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
