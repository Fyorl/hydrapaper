from gettext import gettext as _
from gi.repository import Gdk
from subprocess import run, PIPE
import json
from .get_desktop_environment import get_desktop_environment
from .confManager import ConfManager
from .wallpaper_merger import get_combined_resolution
import dbus
from os import environ as Env


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
        return (
            'HydraPaper Monitor Object: '
            f'Name: {self.name}; '
            f'Resolution: {self.width} x {self.height}; '
            f'Scaling: {self.scaling}; '
            f'Offset: {self.offset_x} x {self.offset_y}; '
            f'Wallpaper path: {self.wallpaper}; '
            f'Mode: {self.mode}; '
            f'Spanned: {self.spanned}.'
        )


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


def get_layout_mode():
    if (Env.get('XDG_SESSION_TYPE') == 'x11'):
        return 1
    elif get_desktop_environment() == 'gnome':
        bus = dbus.SessionBus()
        object_display_config = bus.get_object(
            'org.gnome.Mutter.DisplayConfig',
            '/org/gnome/Mutter/DisplayConfig'
        )
        interface_display_config = dbus.Interface(
            object_display_config,
            dbus_interface='org.gnome.Mutter.DisplayConfig'
        )
        state = interface_display_config.GetCurrentState()
        return state[3].get('layout-mode')
    else:
        return 1

def build_monitors_from_gdk():
    monitors = []
    num_monitors = 0
    max_scale_factor = 0
    try:
        display = Gdk.Display.get_default()
        monitors = list(display.get_monitors())
        num_monitors = len(monitors)
    except Exception:
        print(_('Error parsing monitors (Gdk)'))
        import traceback
        traceback.print_exc()
        monitors = None
        return

    res = list()
    for i in range(num_monitors):
        rect = monitors[i].get_geometry()
        res.append(Monitor(
            rect.width, rect.height,
            monitors[i].get_scale_factor(),
            rect.x, rect.y,
            i,
            f'Monitor {i} ({monitors[i].get_model()})',
            'zoom',
            i == 0  # first monitor will be the primary, doesn't mean much
        ))

    layout_mode = get_layout_mode()

    if layout_mode == 1:
        max_scale_factor = max([r.scaling for r in res])
        for r in res:
            r.height *= max_scale_factor
            r.width *= max_scale_factor
            r.offset_x *= max_scale_factor
            r.offset_y *= max_scale_factor
    return res


def build_monitors_autodetect():
    desktop_environment = get_desktop_environment()
    if desktop_environment == 'sway':
        return build_monitors_from_swaymsg()
    else:
        return build_monitors_from_gdk()


def build_combined_spanned_monitor(monitors=None):
    if monitors is None:
        monitors = build_monitors_autodetect()
    return Monitor(
        *get_combined_resolution(monitors),
        1, 0, 0, 0,
        _('Combined spanned monitor'),
        'zoom',
        True, True
    )
