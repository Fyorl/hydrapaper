from threading import Thread
from gi.repository import Gtk, GLib
from hashlib import sha256
from os.path import isfile
from .wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_mate,
    set_wallpaper_sway,
    multi_setup_pillow,
    cut_image
)
from .confManager import ConfManager
from .get_desktop_environment import get_desktop_environment

def widgets_set_sensitive(widgets, state: bool):
    for w in widgets:
        w.set_sensitive(state)

def _apply_wallpapers_worker(monitors, widgets_to_freeze=[], lockscreen=False):
    confman = ConfManager()
    desktop_environment = get_desktop_environment()
    set_wallpaper = set_wallpaper_gnome
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    elif desktop_environment == 'sway':
        set_wallpaper_sway(monitors, lockscreen)
        GLib.idle_add(widgets_set_sensitive, widgets_to_freeze, True)
        return
    # add other DE cases as `elif` here
    wp_fname = 'merged_wallpaper'
    if confman.conf['random_wallpapers_names']:
        wp_fname = sha256(
            '_'.join([m.__repr__() for m in monitors]).encode()
        ).hexdigest()
    save_path = '{0}/{1}{2}.png'.format(
        confman.cache_path,
        'lockscreen_'
        if lockscreen
        and not confman.conf['random_wallpapers_names']
        else '',
        wp_fname
    )
    if len(monitors) == 1:
        cut_image(
            monitors[0].wallpaper,
            (monitors[0].width, monitors[0].height),
            save_path
        )
        set_wallpaper(
            save_path,
            'spanned' if monitors[0].spanned else 'zoom',
            lockscreen
        )
        GLib.idle_add(widgets_set_sensitive, widgets_to_freeze, True)
        return
    if not confman.conf['random_wallpapers_names'] or not isfile(save_path):
        multi_setup_pillow(monitors, save_path)
    set_wallpaper(save_path, lockscreen=lockscreen)
    GLib.idle_add(widgets_set_sensitive, widgets_to_freeze, True)


def apply_wallpapers(monitors, widgets_to_freeze=[], lockscreen=False):
    t = Thread(
        group=None,
        target=_apply_wallpapers_worker,
        name=None,
        args=(monitors, widgets_to_freeze, lockscreen)
    )
    widgets_set_sensitive(widgets_to_freeze, False)
    t.start()
