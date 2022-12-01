#!@PYTHON@

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from os.path import isfile
from os import environ as Env
import json
import os
from hydrapaper.monitor_parser import (
    build_monitors_autodetect,
    build_combined_spanned_monitor
)
from hydrapaper.apply_wallpapers import apply_wallpapers
from itertools import cycle
from threading import Thread, Event
from sys import exit
from time import sleep


is_flatpak = (
    'XDG_RUNTIME_DIR' in Env.keys() and
    isfile(f'{Env["XDG_RUNTIME_DIR"]}/flatpak-info')
)
CONFIG_PATH = '{0}/org.gabmus.hydrapaper.json'.format(
    os.getenv('XDG_CONFIG_HOME', f'{Env.get("HOME")}/.config')
)

PACKAGE = 'org.gabmus.hydrapaper.Daemon'


class HydrapaperDaemonDisabledException(Exception):
    pass


class HydrapaperDaemon(dbus.service.Object):
    def __init__(self, bus_name):
        super().__init__(
            bus_name,
            f'/{PACKAGE.replace(".", "/")}'
        )
        self.config = None
        self.thread = None
        self.thread_wait_event = None
        self.cycling_wallpapers = None
        self.stop_thread = False
        # dummy window to let Gdk detect the monitors
        self.dummy_window = Gtk.Window()
        self.monitors = None
        self.connect_monitor_changes()
        self.update_config()

    def connect_monitor_changes(self):
        bus = dbus.SessionBus()
        bus.add_signal_receiver(
            self.on_monitors_changed, 'MonitorsChanged', None,
            'org.gnome.Mutter.DisplayConfig', None
        )

    def on_monitors_changed(self, *args):
        print('Monitors change detected')

        def af():
            sleep(2)
            tries = 0
            n_monitors = build_monitors_autodetect()
            while not self.monitors_is_changed(n_monitors) and tries < 10:
                sleep(1)
                tries += 1
                n_monitors = build_monitors_autodetect()
            self.update_monitors(n_monitors)
            self.update_config()
            self.update_monitors_from_config_and_set_wallpapers()
            # self.set_wallpapers()

        Thread(target=af, daemon=True).start()

    def update_monitors_from_config_and_set_wallpapers(self):
        if (
            self.config['Daemon']['wallpaper_rotation_enabled'] and
            len(self.config['Daemon']['rotating_wallpapers']) > 0
        ):
            self.update_thread()
            return
        last_wps = self.config.get('last_wps', None)
        if last_wps is not None and len(last_wps.get('wps', {})) > 0:
            if last_wps.get('spanned', False):
                virt_monitor = build_combined_spanned_monitor(
                    self.monitors, skip_save=True
                )
                fwp = list(last_wps['wps'].values())[0]
                virt_monitor.wallpaper = fwp['wp']
                virt_monitor.mode = fwp.get('mode', 'zoom')
                apply_wallpapers([virt_monitor])
                return
            for m in self.monitors:
                cm = last_wps['wps'].get(
                    m.name, {'wp': m.wallpaper, 'mode': m.mode}
                )
                m.wallpaper = cm['wp']
                m.mode = cm['mode']
        apply_wallpapers(self.monitors, skip_save=True)

    @dbus.service.method(
            dbus_interface=PACKAGE,
            in_signature='', out_signature='b'
    )
    def update_config(self) -> bool:
        if not isfile(CONFIG_PATH):
            return False
        config = None
        with open(CONFIG_PATH, 'r') as fd:
            config = json.loads(fd.read())
        if not config.get('enable_daemon', False):
            raise HydrapaperDaemonDisabledException
        if 'Daemon' not in config.keys():
            return False
        self.config = config
        self.update_thread()
        return True

    def update_thread(self):
        if self.thread is not None:
            self.stop_thread = True
            self.thread_wait_event.set()  # stop event.wait
            self.thread.join()
            self.thread = None
        if self.config['Daemon']['wallpaper_rotation_enabled'] and \
                len(self.config['Daemon']['rotating_wallpapers']) > 0:
            self.cycling_wallpapers = cycle(
                self.config['Daemon']['rotating_wallpapers']
            )
            self.thread_wait_event = Event()
            self.thread = Thread(target=self._thread_worker, daemon=True)
            self.stop_thread = False
            self.thread.start()

    def _thread_worker(self):
        while True:
            if self.stop_thread:
                self.stop_thread = False
                break
            if self.cycling_wallpapers is not None:
                current = next(self.cycling_wallpapers)
                self.set_wallpapers(
                    [c['wallpaper'] for c in current],
                    [c['mode'] for c in current],
                    single_spanned=current[0]['single_spanned']
                )
            self.thread_wait_event.wait(
                timeout=self.config['Daemon']['wallpaper_rotation_sleep_time']
            )

    def monitor_to_comparable_str(self, m):
        return f'{m.name}-{m.width}x{m.height}+{m.offset_x}+{m.offset_y}'

    def monitors_is_changed(self, n_monitors):
        return (
            self.monitors is None or
            len(n_monitors) != len(self.monitors) or
            set(
                [self.monitor_to_comparable_str(m) for m in self.monitors]
            ) != set(
                [self.monitor_to_comparable_str(m) for m in n_monitors]
            )
        )

    def update_monitors(self, n_monitors):
        if self.monitors is not None:
            old = cycle([(m.wallpaper, m.mode) for m in self.monitors])
            for m in n_monitors:
                m.wallpaper, m.mode = next(old)
        self.monitors = n_monitors

    def set_wallpapers(self, wp_paths=None, modes=None, single_spanned=False):
        n_monitors = build_monitors_autodetect()
        if self.monitors_is_changed(n_monitors):
            self.update_monitors(n_monitors)
        if wp_paths is not None:
            if single_spanned:
                for m in self.monitors:
                    m.wallpaper = wp_paths[0]
                virt_monitor = build_combined_spanned_monitor(self.monitors)
                virt_monitor.wallpaper = wp_paths[0]
                apply_wallpapers(
                    [virt_monitor],
                    lockscreen=False, force_random_name=True,
                    skip_save=True
                )
                return
            cycle_wps = cycle(wp_paths)
            while len(wp_paths) < len(self.monitors):
                wp_paths.append(next(cycle_wps))
            if modes is None:
                modes = [m.mode for m in self.monitors]
            for monitor, mode, wp in zip(self.monitors, modes, wp_paths):
                if mode not in ('zoom', 'fit_black', 'fit_blur',
                                'center_black', 'center_blur'):
                    monitor.mode = 'zoom'
                else:
                    monitor.mode = mode
                monitor.wallpaper = wp
        elif None in [m.wallpaper for m in self.monitors]:
            return
        apply_wallpapers(
            self.monitors, lockscreen=False, force_random_name=True,
            skip_save=True
        )


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    try:
        bus_name = dbus.service.BusName(
            PACKAGE, bus=dbus.SessionBus(), do_not_queue=True
        )
    except dbus.exceptions.NameExistsException:
        print('HydrapaperDaemon: service is already running')
        exit(1)
    loop = GLib.MainLoop()
    daemon = HydrapaperDaemon(bus_name)
    try:
        loop.run()
    except KeyboardInterrupt:
        print('HydrapaperDaemon: KeyboardInterrupt received')
    except HydrapaperDaemonDisabledException:
        print('HydrapaperDaemon: Daemon disabled, exiting...')
    except Exception as e:
        print('HydrapaperDaemon: Unhandled exception: `{}`'.format(str(e)))
    finally:
        loop.quit()
