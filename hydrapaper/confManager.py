from .singleton import Singleton
from gi.repository import GObject
from pathlib import Path
from os.path import isfile, isdir
from os import makedirs
from os import environ as Env
import json

class ConfManagerSignaler(GObject.Object):
    __gsignals__ = {
        'hydrapaper_flowbox_selection_mode_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        )
    }

class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'wallpapers_paths': [
            'path': f'{Env.get("HOME")}/Pictures',
            'active': True
        ],
        'selection_mode': 'single',
        'monitors': {},
        'favorites': [],
        'favorites_in_mainview': True,
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
        else:
            self.path = Path(f'{Env.get("HOME")}/.config/org.gabmus.hydrapaper.json')

        self.conf = None
        if isfile(self.path):
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
        else:
            self.conf = self.BASE_SCHEMA.copy()

    def save_conf(self):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()
