from gettext import gettext as _
from os import environ as Env
from os.path import isfile
from threading import Thread
from gi.repository import Gtk
from .wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_mate,
    multi_setup_pillow
)
from .confManager import ConfManager

def _apply_wallpapers_worker(monitors, lockscreen = False):
    confman = ConfManager()
    desktop_environment = Env.get('XDG_CURRENT_DESKTOP').lower()
    set_wallpaper = set_wallpaper_gnome
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    # add other DE cases as `elif` here
    if len(monitors) == 1:
        set_wallpaper(monitors[0].wallpaper, 'zoom', lockscreen)
        return
    wp_unique_str = '_'.join([m.__repr__() for m in monitors])
    save_path = '{0}/merged_wallpaper.png'.format(
        confman.cache_path
    )
    multi_setup_pillow(monitors, save_path)
    set_wallpaper(save_path, lockscreen = lockscreen)


def apply_wallpapers(monitors, widgets_to_freeze = [], lockscreen = False):
    t = Thread(
        group = None,
        target = _apply_wallpapers_worker,
        name = None,
        args = (monitors, lockscreen)
    )
    for w in widgets_to_freeze:
        w.set_sensitive(False)
    t.start()
    while t.is_alive():
        while Gtk.events_pending():
            Gtk.main_iteration()
    for w in widgets_to_freeze:
        w.set_sensitive(True)
