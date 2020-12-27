from gi.repository import GLib
import dbus
from os.path import isfile, environ as Env
import json
from hydrapaper.monitor_parser import build_monitors_autodetect
from hydrapaper.apply_wallpapers import apply_wallpapers
from itertools import cycle
from threading import Thread, Event
from sys import exit


is_flatpak = (
    'XDG_RUNTIME_DIR' in Env.keys() and
    isfile(f'{Env["XDG_RUNTIME_DIR"]}/flatpak-info')
)
CONFIG_PATH = '{0}/org.gabmus.hydrapaper.json'.format(
    Env.get('XDG_CONFIG_HOME') if is_flatpak
    else Env.get('HOME') + '/.config'
)

PACKAGE = 'org.gabmus.hydrapaper.Daemon'


class HydrapaperDaemon(dbus.service.Object):
    def __init__(self, bus_name):
        super().__init__(bus_name, f'/{PACKAGE.replace(".", "/")}')
        self.config = None
        self.thread = None
        self.thread_wait_event = Event()
        self.cycling_wallpapers = None
        self.stop_thread = False
        self.update_config()

    @dbus.service.method(
            dbus_interface=PACKAGE+'.update_config',
            in_signature='', out_signature='b'
    )
    def update_config(self) -> bool:
        if not isfile(CONFIG_PATH):
            return False
        config = None
        with open(CONFIG_PATH, 'r') as fd:
            config = json.loads(fd.read())
        if 'Daemon' not in config.keys():
            return False
        self.config = config
        self.update_thread()
        return True

    def update_thread(self):
        if self.thread is not None:
            if not self.config['Daemon']['wallpaper_rotation_enabled']:
                self.stop_thread = True
                self.thread_wait_event.set()
                self.thread.join()
                self.thread = None
            else:
                self.thread_wait_event.set()  # stop event.wait
        if self.config['Daemon']['wallpaper_rotation_enabled'] and \
                len(self.config['Daemon']['rotating_wallpapers']) > 0:
            self.cycling_wallpapers = cycle(
                self.config['Daemon']['rotating_wallpapers']
            )
            self.thread = Thread(target=self._thread_worker, daemon=True)
            self.stop_thread = False
            self.thread.start()

    def _thread_worker(self):
        while True:
            if self.stop_thread:
                self.stop_thread = False
                break
            if self.cycling_wallpapers is not None:
                self.set_wallpapers(next(self.cycling_wallpapers))
            self.thread_wait_event.wait(
                timeout=self.config['Daemon']['wallpaper_rotation_sleep_time']
            )

    def set_wallpapers(self, wp_paths, modes=None):
        monitors = build_monitors_autodetect()
        cycle_wps = cycle(wp_paths)
        while len(wp_paths) < len(monitors):
            wp_paths.append(next(cycle_wps))
        if modes is None:
            modes = ['zoom' for i in range(len(monitors))]
        for monitor, mode, wp in zip(monitors, modes, wp_paths):
            if mode not in ('zoom', 'fit_black', 'fit_blur',
                            'center_black', 'center_blur'):
                monitor.mode = 'zoom'
            else:
                monitor.mode = mode
            monitor.wallpaper = wp
        apply_wallpapers(monitors, lockscreen=False)


if __name__ == '__main__':
    daemon = HydrapaperDaemon()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    try:
        bus_name = dbus.service.BusName(
            PACKAGE, bus=dbus.SessionBus(), do_not_queue=True
        )
    except dbus.exceptions.NameExistsException:
        print('HydrapaperDaemon: service is already running')
        exit(1)
    try:
        loop.run()
    except KeyboardInterrupt:
        print('HydrapaperDaemon: KeyboardInterrupt received')
    except Exception as e:
        print('HydrapaperDaemon: Unhandled exception: `{}`'.format(str(e)))
    finally:
        loop.quit()
