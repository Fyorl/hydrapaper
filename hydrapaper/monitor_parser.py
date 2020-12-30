from gettext import gettext as _
from gi.repository import Gdk
from subprocess import run, PIPE
import json
from .get_desktop_environment import get_desktop_environment
from .confManager import ConfManager


confman = ConfManager()


class Monitor:
    def __init__(
            self,
            width,
            height,
            scaling,
            offset_x,
            offset_y,
            index,
            name,
            mode='zoom',
            primary=False,
            spanned=False
    ):
        self.width = int(width)
        self.height = int(height)
        self.scaling = int(scaling)
        self.primary = primary
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.index = index
        self.name = name
        self.mode = mode
        self.wallpaper = None
        self.spanned = spanned

        if self.name in confman.conf['monitors'].keys():
            self.wallpaper = \
                confman.conf['monitors'][self.name]['wallpaper']
            self.mode = confman.conf['monitors'][self.name]['mode']

    def __repr__(self):
        return f'''\nHydraPaper Monitor Object
- Name: {self.name}
- Resolution: {self.width} x {self.height}
- Scaling: {self.scaling}
- Offset: {self.offset_x} x {self.offset_y}
- Wallpaper path: {self.wallpaper}
- Mode: {self.mode}
- Spanned: {self.spanned}
'''


def build_monitors_from_swaymsg():
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
            'zoom',
            out['primary']
        ) for i, out in enumerate(outputs)
    ]
    return monitors


def build_monitors_from_gdk():
    monitors = []
    num_monitors = 0
    try:
        display = Gdk.Display.get_default()
        monitors = list(display.get_monitors())
        num_monitors = len(monitors)
    except Exception:
        print(_('Error parsing monitors (Gdk)'))
        import traceback
        traceback.print_exc()
        monitors = None

    def get_monitor_rect(i):
        return monitors[i].get_geometry()

    monitors = [
        Monitor(
            get_monitor_rect(i).width,
            get_monitor_rect(i).height,
            monitors[i].get_scale_factor(),
            get_monitor_rect(i).x,
            get_monitor_rect(i).y,
            i,
            f'Monitor {i} ({monitors[i].get_model()})',
            'zoom',
            i == 0  # is_primary is no more, I'll considered first primary now
        ) for i in range(0, num_monitors)
    ]
    return monitors


def build_monitors_autodetect():
    desktop_environment = get_desktop_environment()
    if desktop_environment == 'sway':
        return build_monitors_from_swaymsg()
    else:
        return build_monitors_from_gdk()
