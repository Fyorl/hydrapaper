# __main__.py
#
# Copyright (C) 2019 GabMus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gettext import gettext as _
import sys
import argparse
from gi.repository import Gtk, Gdk, Gio, Handy
from .confManager import ConfManager
from .app_window import HydraPaperAppWindow
from .settings_box import HydraPaperSettingsWindow
from .is_image import is_image
from .monitor_parser import build_monitors_autodetect
from .apply_wallpapers import apply_wallpapers

class HydraPaperApplication(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(
            application_id = 'org.gabmus.hydrapaper',
            flags = Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.confman = ConfManager()
        self.window = HydraPaperAppWindow()
        self.window.connect('destroy', self.on_destroy_window)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Handy.init()
        actions = [
            {
                'name': 'set_random_wallpaper',
                'func': lambda *args: self.apply_random(),
                'accel': '<Primary><Shift>r'
            },
            {
                'name': 'settings',
                'func': self.show_settings_window,
                'accel': '<Primary>comma'
            },
            {
                'name': 'shortcuts',
                'func': self.show_shortcuts_window,
                'accel': '<Primary>question'
            },
            {
                'name': 'about',
                'func': self.show_about_dialog
            },
            {
                'name': 'quit',
                'func': self.on_destroy_window,
                'accel': '<Primary>q'
            }
        ]

        for a in actions:
            c_action = Gio.SimpleAction.new(a['name'], None)
            c_action.connect('activate', a['func'])
            self.add_action(c_action)
            if 'accel' in a.keys():
                self.set_accels_for_action(
                    f'app.{a["name"]}',
                    [a['accel']]
                )

    def show_about_dialog(self, *args):
        about_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/aboutdialog.glade'
        )
        dialog = about_builder.get_object('aboutdialog')
        dialog.set_modal(True)
        dialog.set_transient_for(self.window)
        dialog.present()

    def on_destroy_window(self, *args):
        self.window.on_destroy()
        self.quit()

    def show_shortcuts_window(self, *args):
        shortcuts_win = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/shortcutsWindow.xml'
        ).get_object('shortcuts-hydrapaper')
        shortcuts_win.props.section_name = 'shortcuts'
        shortcuts_win.set_transient_for(self.window)
        # shortcuts_win.set_attached_to(self.window)
        shortcuts_win.set_modal(True)
        shortcuts_win.present()
        shortcuts_win.show_all()

    def show_settings_window(self, *args):
        settings_win = HydraPaperSettingsWindow()
        settings_win.set_transient_for(self.window)
        # settings_win.set_attached_to(self.window)
        settings_win.set_modal(True)
        settings_win.present()

    def apply_random(self, lockscreen=False):
        from random import randint
        monitors = build_monitors_autodetect()
        all_wallpapers = self.confman.wallpapers
        wallpapers = [
            all_wallpapers[
                randint(0,len(all_wallpapers)-1)
            ] for i in range(len(monitors))
        ]
        self.apply_from_cli(wallpapers, lockscreen)

    def apply_from_cli(self, wlist_cli, lockscreen=False):
        # check all the passed wallpapers to be correct
        monitors = build_monitors_autodetect()
        if len(wlist_cli) < len(monitors):
            print(
                _('Error: you passed {0} wallpapers for {1} monitors').format(
                    len(wlist_cli), len(monitors)
                )
            )
            exit(1)
        for wpath in wlist_cli:
            if not is_image(wpath):
                print(_('Error: {0} is not a valid image path').format(wpath))
                exit(1)
        for monitor, n_wp in zip(monitors, wlist_cli):
            monitor.wallpaper = n_wp
        n_monitors = {}
        for m in monitors:
            n_monitors[m.name] = m.wallpaper
        self.confman.conf['monitors'] = n_monitors
        self.confman.save_conf()
        apply_wallpapers(monitors, lockscreen=lockscreen)

    def do_activate(self):
        self.add_window(self.window)
        stylecontext = Gtk.StyleContext()
        provider = Gtk.CssProvider()
        provider.load_from_data('''
            .wallpapers-flowbox {
                padding-top: 24px;
            }
        '''.encode())
        stylecontext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        if self.args:
            if self.args.wallpaper_path:
                self.apply_from_cli(self.args.wallpaper_path[0], self.args.set_lockscreen)
                self.quit()
                exit(0)
            if self.args.set_random:
                self.apply_random(self.args.set_lockscreen)
                self.quit()
                exit(0)
        self.window.present()
        self.window.show_all()

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        Gtk.Application.do_command_line(self, args)  # call the default commandline handler
        # make a command line parser
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--cli', dest='wallpaper_path', nargs='+', action='append', help=_('set wallpapers from command line'))
        parser.add_argument('-r', '--random', dest='set_random', action='store_true', help=_('set wallpapers randomly'))
        parser.add_argument('-l', '--lockscreen', dest='set_lockscreen', action='store_true', help=_('set lockscreen wallpapers instead of desktop ones'))
        # parse the command line stored in args, but skip the first element (the filename)
        self.args = parser.parse_args(args.get_arguments()[1:])
        # call the main program do_activate() to start up the app
        self.do_activate()
        return 0

def main():
    application = HydraPaperApplication()

    try:
        ret = application.run(sys.argv)
    except SystemExit as e:
        ret = e.code

    sys.exit(ret)


if __name__ == '__main__':
    main()
