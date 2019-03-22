from .singleton import Singleton
from pathlib import Path
from os.path import isfile, isdir
from os import makedirs
from os import environ as Env
import json

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

        # check if inside flatpak sandbox
        self.is_flatpak = False
        if 'XDG_RUNTIME_DIR' in Env.keys():
            if isfile(f'{Env["XDG_RUNTIME_DIR"]}/flatpak-info'):
                self.is_flatpak = True

        if self.is_flatpak:
            self.path = Path(f'{Env.get("XDG_CONFIG_HOME")}/org.gabmus.unifydmin.json')
        else:
            self.path = Path(f'{Env.get("HOME")}/.config/org.gabmus.unifydmin.json')
