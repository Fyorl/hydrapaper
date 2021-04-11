from gettext import gettext as _
from gi.repository import Gtk, Adw
from .confManager import ConfManager
from os.path import isfile, abspath, join
from os import remove, listdir
from os import environ as Env
from subprocess import run
from .daemon_helper import APPLICATIONS_DIR, DAEMON_BUILD_ENABLED


class PreferencesButtonRow(Adw.ActionRow):
    """
    A preferences row with a title and a button
    title: the title shown
    button_label: a label to show inside the button
    onclick: the function that will be called when the button is pressed
    button_style_class: the style class of the button.
    Common options: `suggested-action`, `destructive-action`
    signal: an optional signal to let ConfManager emit when the
    button is pressed
    """
    def __init__(
            self, title, button_label, onclick, button_style_class=None,
            signal=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.button_label = button_label
        self.confman = ConfManager()
        self.set_title(self.title)
        self.signal = signal
        self.onclick = onclick

        self.button = Gtk.Button()
        self.button.set_label(self.button_label)
        self.button.set_valign(Gtk.Align.CENTER)
        if button_style_class:
            self.button.get_style_context().add_class(button_style_class)
        self.button.connect('clicked', self.on_button_clicked)
        self.add_suffix(self.button)
        # You need to press the actual button
        # Avoids accidental presses
        # self.set_activatable_widget(self.button)

    def on_button_clicked(self, button):
        self.onclick(self.confman)
        if self.signal:
            self.confman.emit(self.signal, '')
        self.confman.save_conf()


class PreferencesToggleRow(Adw.ActionRow):
    """
    A preferences row with a title and a toggle
    title: the title shown
    conf_key: the key of the configuration dictionary/json in ConfManager
    signal: an optional signal to let ConfManager emit when the configuration
    is set
    """
    def __init__(
            self, title, conf_key, signal=None, subtitle=None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.confman = ConfManager()
        self.set_title(self.title)
        if subtitle:
            self.subtitle = subtitle
            self.set_subtitle(self.subtitle)
        self.conf_key = conf_key
        self.signal = signal

        self.toggle = Gtk.Switch()
        self.toggle.set_valign(Gtk.Align.CENTER)
        if self.conf_key is not None:
            self.toggle.set_active(self.confman.conf[self.conf_key])
        self.toggle.connect('state-set', self.on_toggle_state_set)
        self.add_suffix(self.toggle)
        self.set_activatable_widget(self.toggle)

    def on_toggle_state_set(self, toggle, state):
        if self.conf_key is not None:
            self.confman.conf[self.conf_key] = state
            self.confman.save_conf()
        if self.signal:
            self.confman.emit(self.signal, '')


class AutostartToggleRow(PreferencesToggleRow):
    def __init__(self):
        super().__init__(
            _('Start daemon on login'),
            None, None,
            _('React to monitor changes and start slideshow mode')
        )
        self.source_file = \
            f'{APPLICATIONS_DIR}/org.gabmus.hydrapaper.Daemon.desktop'
        self.autostart_dir = \
            f'{Env.get("HOME")}/.config/autostart'
        self.target_file = \
            f'{self.autostart_dir}/org.gabmus.hydrapaper.Daemon.desktop'
        self.toggle.set_active(self.target_exists())

    def target_exists(self):
        if isfile(self.target_file):
            with open(self.target_file, 'r') as fd:
                if fd.read().strip() != self.get_daemon_desktop_file().strip():
                    self.create_autostart()
                return True
        return False

    def get_daemon_desktop_file(self):
        res = ''
        with open(self.source_file, 'r') as fd:
            res = fd.read()
        if self.confman.is_flatpak:
            res = res.replace(
                '/app/libexec/hydrapaperd',
                '/usr/bin/flatpak run --command=/app/libexec/hydrapaperd '
                'org.gabmus.hydrapaper'
            )
        return res

    def create_autostart(self):
        self.delete_autostart()
        cmds = [
            f'mkdir -p {self.autostart_dir}',
            (
                f"cat <<'EOF' >> {self.target_file}\n"
                f"{self.get_daemon_desktop_file()}\nEOF"
            )
        ]
        for cmd in cmds:
            if self.confman.is_flatpak:
                cmd = 'flatpak-spawn --host ' + cmd
            run(cmd, shell=True)

    def delete_autostart(self):
        if isfile(self.target_file):
            remove(self.target_file)

    def on_toggle_state_set(self, toggle, state):
        if state:
            self.create_autostart()
        else:
            self.delete_autostart()


class GeneralPreferencesPage(Adw.PreferencesPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_('General'))
        self.set_icon_name('preferences-other-symbolic')

        self.general_preferences_group = Adw.PreferencesGroup()
        self.general_preferences_group.set_title(_('General Settings'))
        toggle_settings = [
            {
                'title': _('Save each wallpaper separately'),
                'subtitle': _(
                    'Warning: this feature will use a lot of disk space\n'
                    'Periodically clear the cache to mitigate this problem'
                ),
                'conf_key': 'random_wallpapers_names',
            }
        ]
        if DAEMON_BUILD_ENABLED:
            toggle_settings.append(
                {
                    'title': _('Enable daemon'),
                    'subtitle': _(
                        'Needed for slideshow mode and to detect display '
                        'changes'
                    ),
                    'conf_key': 'enable_daemon',
                }
            )
        for s in toggle_settings:
            row = PreferencesToggleRow(
                s['title'],
                s['conf_key'],
                signal=s.get('signal'),
                subtitle=s.get('subtitle')
            )
            self.general_preferences_group.add(row)
        if DAEMON_BUILD_ENABLED:
            self.general_preferences_group.add(AutostartToggleRow())
        self.add(self.general_preferences_group)

        self.caches_favs_preferences_group = Adw.PreferencesGroup()
        self.caches_favs_preferences_group.set_title(_('Caches and favorites'))
        button_settings = [
            {
                'title': _('Clear all favorites'),
                'button_label': _('Clear favorites'),
                'onclick': self.clear_favorites,
                'button_style_class': 'destructive-action',
                'signal': 'hydrapaper_populate_wallpapers'
            },
            {
                'title': _('Clear all caches'),
                'button_label': _('Clear caches'),
                'onclick': self.clear_caches,
                'button_style_class': 'destructive-action',
                'signal': 'hydrapaper_populate_wallpapers'
            }
        ]
        for s in button_settings:
            row = PreferencesButtonRow(
                s['title'],
                s['button_label'],
                s['onclick'],
                s['button_style_class'],
                s['signal']
            )
            self.caches_favs_preferences_group.add(row)
        self.add(self.caches_favs_preferences_group)

        self.show()

    def clear_favorites(self, confman, *args):
        confman.conf['favorites'] = []

    def clear_caches(self, confman, *args):
        for p in [confman.cache_path, confman.thumbs_cache_path]:
            files = [
                abspath(join(p, f)) for f in listdir(p)
            ]
            for f in files:
                if isfile(f):
                    remove(f)


class ViewPreferencesPage(Adw.PreferencesPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_('View'))
        self.set_icon_name('applications-graphics-symbolic')

        self.view_preferences_group = Adw.PreferencesGroup()
        self.view_preferences_group.set_title(_('View Settings'))
        toggle_settings = [
            {
                'title': _('Use big thumbnails for the monitors previews'),
                'conf_key': 'big_monitor_thumbnails',
                'signal': 'hydrapaper_reload_monitor_thumbs'
            },
            {
                'title': _('Show full path in folder view'),
                'conf_key': 'folders_popover_full_path',
                'signal': 'hydrapaper_set_folders_popover_labels'
            }
        ]
        for s in toggle_settings:
            row = PreferencesToggleRow(s['title'], s['conf_key'], s['signal'])
            self.view_preferences_group.add(row)
        self.add(self.view_preferences_group)

        self.show()


class HydraPaperSettingsWindow(Adw.PreferencesWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pages = [
            GeneralPreferencesPage(),
            ViewPreferencesPage()
        ]
        for p in self.pages:
            self.add(p)

        self.set_default_size(640, 700)
