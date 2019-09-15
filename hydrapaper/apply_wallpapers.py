from os import environ as Env
from threading import Thread
from gi.repository import Gtk
from .wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_mate,
    set_wallpaper_sway,
    multi_setup_pillow
)
from .confManager import ConfManager


def _apply_wallpapers_worker(monitors, lockscreen=False):
    confman = ConfManager()
    desktop_environment = (
        Env.get('XDG_CURRENT_DESKTOP') or
        Env.get('XDG_SESSION_DESKTOP') or
        Env.get('DESKTOP_SESSION') or
        ''
    ).lower()
    set_wallpaper = set_wallpaper_gnome
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    elif desktop_environment == 'sway':
        set_wallpaper_sway(monitors, lockscreen)
        return
    # add other DE cases as `elif` here
    if len(monitors) == 1:
        set_wallpaper(monitors[0].wallpaper, 'zoom', lockscreen)
        return
    save_path = '{0}/{1}merged_wallpaper.png'.format(
        confman.cache_path,
        'lockscreen_' if lockscreen else ''
    )
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
