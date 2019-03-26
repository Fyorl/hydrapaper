from os import environ as Env
from os.path import isfile
from hashlib import sha256
from threading import Thread
from gi.repository import Gtk
from .wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_mate,
    multi_setup_pillow
)
from .confManager import ConfManager

def _apply_wallpapers_worker(monitors):
    confman = ConfManager()
    desktop_environment = Env.get('XDG_CURRENT_DESKTOP').lower()
    set_wallpaper = set_wallpaper_gnome
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    # add other DE cases as `elif` here
    if len(monitors) == 1:
        set_wallpaper(monitors[0].wallpaper, 'zoom')
        return
    wp_unique_str = '_'.join([m.__repr__() for m in monitors])
    save_path = '{0}/{1}.png'.format(
        confman.cache_path,
        sha256(
            f'HydraPaper{wp_unique_str}'.encode()
        ).hexdigest()
    )
    if isfile(save_path):
        print(f'Hit cache for {save_path}. Skipping merge')
    else:
        multi_setup_pillow(monitors, save_path)
    set_wallpaper(save_path)


def apply_wallpapers(monitors, widgets_to_freeze = [], spinner = None):
    t = Thread(
        group = None,
        target = _apply_wallpapers_worker,
        name = None,
        args = (monitors,)
    )
    for w in widgets_to_freeze:
        w.set_sensitive(False)
    if spinner:
        spinner.start()
    t.start()
    while t.is_alive():
        while Gtk.events_pending():
            Gtk.main_iteration()
    for w in widgets_to_freeze:
        w.set_sensitive(True)
    if spinner:
        spinner.stop()
