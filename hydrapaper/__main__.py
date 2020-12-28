from gettext import gettext as _
import sys
import argparse
from gi.repository import Gtk, Gdk, Gio, GLib, Handy
from .confManager import ConfManager
from .app_window import HydraPaperAppWindow
from .settings_box import HydraPaperSettingsWindow
from .is_image import is_image
from .monitor_parser import build_monitors_autodetect
from .apply_wallpapers import apply_wallpapers


class HydraPaperApplication(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(
            application_id='org.gabmus.hydrapaper',
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        GLib.set_application_name('HydraPaper')
        GLib.set_prgname('org.gabmus.hydrapaper')
        self.confman = ConfManager()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Handy.init()

    def show_about_dialog(self, *args):
        about_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/aboutdialog.ui'
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
            '/org/gabmus/hydrapaper/ui/shortcutsWindow.ui'
        ).get_object('shortcuts-hydrapaper')
        shortcuts_win.props.section_name = 'shortcuts'
        shortcuts_win.set_transient_for(self.window)
        # shortcuts_win.set_attached_to(self.window)
        shortcuts_win.set_modal(True)
        shortcuts_win.present()
        shortcuts_win.show()

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
                randint(0, len(all_wallpapers)-1)
            ] for i in range(len(monitors))
        ]
        self.apply_from_cli(wallpapers, lockscreen=lockscreen)

    def apply_from_cli(self, wlist_cli, modes=None, lockscreen=False):
        # check all the passed wallpapers to be correct
        monitors = build_monitors_autodetect()
        if len(wlist_cli) < len(monitors):
            print(
                _('Error: you passed {0} wallpapers for {1} monitors').format(
                    len(wlist_cli), len(monitors)
                )
            )
            exit(1)
        if modes is None:
            modes = ['zoom' for i in range(len(monitors))]
        elif len(modes) < len(wlist_cli):
            print(
                _('Error: you passed {0} modes for {1} wallpapers').format(
                    len(modes), len(wlist_cli)
                )
            )
            exit(1)
        for monitor, mode in zip(monitors, modes):
            if mode not in ('zoom', 'fit_black', 'fit_blur',
                            'center_black', 'center_blur'):
                print(
                    _('Error: wallpaper mode {0} is not valid. '
                      'Allowed values are: zoom, fit_black, fit_blur, '
                      'center_black, center_blur').format(
                       mode
                    )
                )
                exit(1)
            monitor.mode = mode
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
        provider = Gtk.CssProvider()
        provider.load_from_data('''
            .wallpapers-flowbox {
                padding-top: 24px;
            }
            .slideshow-btn-inactive > button > image {
                color: @theme_unfocused_fg_color;
            }
            .slideshow-btn-active > button > image {
                color: @success_color;
            }
            .linked button {
                margin-top: 0;
                margin-bottom: 0;
            }
        '''.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        stateful_actions = [
            {
                'name': 'spanned_mode',
                'func': self.toggle_spanned_mode,
                'type': 'bool',
                # 'accel': '<Control>h',
                'confman_key': 'spanned_mode'
            }
        ]
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

        for sa in stateful_actions:
            c_action = None
            if sa['type'] == 'bool':
                c_action = Gio.SimpleAction.new_stateful(
                    sa['name'],
                    None,
                    GLib.Variant.new_boolean(
                        self.confman.conf[sa['confman_key']]
                    )
                )
            elif sa['type'] == 'radio':
                c_action = Gio.SimpleAction.new_stateful(
                    sa['name'],
                    GLib.VariantType.new('s'),
                    GLib.Variant('s', self.confman.conf[sa['confman_key']])
                )
            else:
                raise ValueError(
                    f'Stateful Action: unsupported type `{sa["type"]}`'
                )
            c_action.connect('activate', sa['func'])
            self.add_action(c_action)
            if 'accel' in sa.keys():
                self.set_accels_for_action(
                    f'app.{sa["name"]}',
                    [sa['accel']]
                )

        for a in actions:
            c_action = Gio.SimpleAction.new(a['name'], None)
            c_action.connect('activate', a['func'])
            self.add_action(c_action)
            if 'accel' in a.keys():
                self.set_accels_for_action(
                    f'app.{a["name"]}',
                    [a['accel']]
                )
        self.window = HydraPaperAppWindow()
        self.window.connect('close-request', self.on_destroy_window)
        self.add_window(self.window)
        if self.args:
            if self.args.wallpaper_path:
                self.apply_from_cli(
                    self.args.wallpaper_path[0],
                    self.args.wallpaper_modes[0]
                    if self.args.wallpaper_modes
                    else None,
                    self.args.set_lockscreen
                )
                self.quit()
                exit(0)
            if self.args.set_random:
                self.apply_random(self.args.set_lockscreen)
                self.quit()
                exit(0)
        self.window.present()
        self.window.show()

    def toggle_spanned_mode(self, action: Gio.SimpleAction, *args):
        action.change_state(
            GLib.Variant.new_boolean(not action.get_state().get_boolean())
        )
        self.confman.conf['spanned_mode'] = action.get_state().get_boolean()
        self.confman.emit('hydrapaper_spanned_mode_changed', '')

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        # call the default commandline handler
        Gtk.Application.do_command_line(self, args)
        # make a command line parser
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--cli',
            dest='wallpaper_path',
            nargs='+', action='append',
            help=_('set wallpapers from command line')
        )
        parser.add_argument(
            '-m', '--modes',
            dest='wallpaper_modes',
            nargs='+', action='append',
            help=_('specify the modes for the wallpapers (zoom, center_black, '
                   'center_blur, fit_black, fit_blur)')
        )
        parser.add_argument(
            '-r', '--random',
            dest='set_random',
            action='store_true',
            help=_('set wallpapers randomly')
        )
        parser.add_argument(
            '-l', '--lockscreen',
            dest='set_lockscreen',
            action='store_true',
            help=_('set lockscreen wallpapers instead of desktop ones')
        )
        # parse the command line stored in args,
        # but skip the first element (the filename)
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
