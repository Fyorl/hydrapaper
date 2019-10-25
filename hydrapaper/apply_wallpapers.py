from os import environ as Env
from threading import Thread
from gi.repository import Gtk
from hashlib import sha256
from os.path import isfile
from .wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_mate,
    set_wallpaper_sway,
    multi_setup_pillow
)
from .confManager import ConfManager
from .get_desktop_environment import get_desktop_environment


def _apply_wallpapers_worker(monitors, lockscreen=False):
    confman = ConfManager()
    desktop_environment = get_desktop_environment()
    set_wallpaper = set_wallpaper_gnome
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    elif desktop_environment == 'sway':
        set_wallpaper_sway(monitors, lockscreen)
        return
    # add other DE cases as `elif` here
    wp_fname = 'merged_wallpaper'
    if confman.conf['random_wallpapers_names']:
        wp_fname = sha256(
            '_'.join([m.__repr__() for m in monitors]).encode()
        ).hexdigest()
    if len(monitors) == 1:
        set_wallpaper(monitors[0].wallpaper, 'zoom', lockscreen)
        return
    save_path = '{0}/{1}{2}.png'.format(
        confman.cache_path,
        'lockscreen_' if lockscreen and not confman.conf['random_wallpapers_names'] else '',
        wp_fname
    )
    if not confman.conf['random_wallpapers_names'] or not isfile(save_path):
        multi_setup_pillow(monitors, save_path)
    set_wallpaper(save_path, lockscreen=lockscreen)


def apply_wallpapers(monitors, widgets_to_freeze=[], lockscreen=False):
    t = Thread(
        group=None,
        target=_apply_wallpapers_worker,
        name=None,
        args=(monitors, lockscreen)
    )
    for w in widgets_to_freeze:
        w.set_sensitive(False)
    t.start()
    while t.is_alive():
        while Gtk.events_pending():
            Gtk.main_iteration()
    for w in widgets_to_freeze:
        w.set_sensitive(True)
