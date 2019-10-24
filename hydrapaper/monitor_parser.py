from gettext import gettext as _
from gi.repository import Gdk
from subprocess import run, PIPE
import json
from os import environ as Env
from .get_desktop_environment import get_desktop_environment
from .confManager import ConfManager


class Monitor:
    def __init__(self, width, height, scaling, offset_x, offset_y, index, name, primary=False):
        self.width = int(width)
        self.height = int(height)
        self.scaling = int(scaling)
        self.primary = primary
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.index = index
        self.name = name
        self.wallpaper = None

    def __repr__(self):
        return f'''HydraPaper Monitor Object
- Name: {self.name};
- Resolution: {self.width} x {self.height};
- Scaling: {self.scaling}
- Offset: {self.offset_x} x {self.offset_y};
- Wallpaper path: {self.wallpaper};'''


def build_monitors_from_swaymsg():
    confman = ConfManager()
    cmd = 'swaymsg -rt get_outputs'
    if confman.is_flatpak:
        cmd = 'flatpak-spawn --host ' + cmd
    res = run(cmd.split(' '), stdout=PIPE)
    outputs = json.loads(res.stdout.decode())
    monitors = [
        Monitor(
            out['rect']['width'],
            out['rect']['height'],
            out['scale'],
            out['rect']['x'],
            out['rect']['y'],
            i,
            out['name'],
            out['primary']
        ) for i, out in enumerate(outputs)
    ]
    return monitors


def build_monitors_from_gdk():
    try:
        display = Gdk.Display.get_default()
        num_monitors = display.get_n_monitors()
    except Exception:
        print(_('Error parsing monitors (Gdk)'))
        import traceback
        traceback.print_exc()
        monitors = None
    get_monitor_rect = lambda i: display.get_monitor(i).get_geometry()
    monitors = [
        Monitor(
            get_monitor_rect(i).width,
            get_monitor_rect(i).height,
            display.get_monitor(i).get_scale_factor(),
            get_monitor_rect(i).x,
            get_monitor_rect(i).y,
            i,
            f'Monitor {i} ({display.get_monitor(i).get_model()})',
            display.get_monitor(i).is_primary()
        ) for i in range(0, num_monitors)
    ]
    print(monitors)
    return monitors


def build_monitors_autodetect():
    desktop_environment = get_desktop_environment()
    if desktop_environment == 'sway':
        return build_monitors_from_swaymsg()
    else:
        return build_monitors_from_gdk()
