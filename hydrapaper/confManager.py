from .singleton import Singleton
from gi.repository import GObject, GLib
from pathlib import Path
from os.path import isfile, isdir
from .is_image import is_image
from os import makedirs, listdir, system
from os import environ as Env
import json

pictures_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
if not pictures_dir:
    system('xdg-user-dirs-update')
    pictures_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
    if not pictures_dir:
        pictures_dir = f'{Env.get("HOME")}/Pictures'

class ConfManagerSignaler(GObject.Object):
    __gsignals__ = {
        'hydrapaper_flowbox_selection_mode_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_flowbox_wallpaper_selected': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_populate_wallpapers': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_show_hide_wallpapers': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_set_folders_popover_labels': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_reload_monitor_thumbs': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        )
    }

class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'wallpapers_paths': [
            {
                'path': pictures_dir,
                'active': True
            }
        ],
        'selection_mode': 'single',
        'monitors': {},
        'favorites': [],
        'favorites_in_mainview': True,
        'folders_popover_full_path': False,
        'big_monitor_thumbnails': True,
        'windowsize': {
            'width': 600,
            'height': 400
        }
    }

    def __init__(self):
        self.signaler = ConfManagerSignaler()
        self.emit = self.signaler.emit
        self.connect = self.signaler.connect

        # check if inside flatpak sandbox
        self.is_flatpak = False
        if 'XDG_RUNTIME_DIR' in Env.keys():
            if isfile(f'{Env["XDG_RUNTIME_DIR"]}/flatpak-info'):
                self.is_flatpak = True

        if self.is_flatpak:
            self.path = Path(f'{Env.get("XDG_CONFIG_HOME")}/org.gabmus.hydrapaper.json')
            self.cache_path = f'{Env.get("XDG_CACHE_HOME")}/hydrapaper'
        else:
            self.path = Path(f'{Env.get("HOME")}/.config/hydrapaper.json')
            self.cache_path = f'{Env.get("HOME")}/.cache/hydrapaper'
        self.thumbs_cache_path = f'{self.cache_path}/thumbnails/'

        self.conf = None
        if isfile(self.path):
            try:
                with open(self.path) as fd:
                    self.conf = json.loads(fd.read())
                    fd.close()
                # verify that the file has all of the schema keys
                for k in self.BASE_SCHEMA.keys():
                    if not k in self.conf.keys():
                        if type(self.BASE_SCHEMA[k]) in [list, dict]:
                            self.conf[k] = self.BASE_SCHEMA[k].copy()
                        else:
                            self.conf[k] = self.BASE_SCHEMA[k]
            except:
                self.conf = self.BASE_SCHEMA.copy()
                self.save_conf()
        else:
            self.conf = self.BASE_SCHEMA.copy()
            self.save_conf()

        for p in [self.cache_path, self.thumbs_cache_path]:
            if not isdir(p):
                makedirs(p)

        self.windows_to_restore = []

        self.wallpapers = []
        self.populate_wallpapers()

    def save_conf(self):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()

    def populate_wallpapers(self):
        self.wallpapers = []
        for index, folder in enumerate(self.conf['wallpapers_paths']):
            if isdir(folder['path']):
                for f in listdir(folder['path']):
                    f_path = f'{folder["path"]}/{f}'
                    if is_image(f_path):
                        self.wallpapers.append(f_path)
            else:
                self.conf['wallpapers_paths'].pop(index)
        self.emit(
            'hydrapaper_populate_wallpapers',
            'notimportant'
        )
