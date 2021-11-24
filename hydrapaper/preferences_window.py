from gettext import gettext as _
from gi.repository import Gtk, Adw
from os.path import isfile, abspath, join
from os import remove, listdir
from os import environ as Env
from subprocess import run
from .daemon_helper import APPLICATIONS_DIR, DAEMON_BUILD_ENABLED
from .base_preferences import (
    MPreferencesPage, MPreferencesGroup,
    PreferencesButtonRow, PreferencesToggleRow
)
from typing import Optional


class AutostartToggleRow(PreferencesToggleRow):
    def __init__(self):
        super().__init__(
            title=_('Start daemon on login'),
            subtitle=_('React to monitor changes and start slideshow mode'),
            conf_key=None
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


class GeneralPreferencesPage(MPreferencesPage):
    def __init__(self):
        general_rows = [
            PreferencesToggleRow(
                title=_('Save each wallpaper separately'),
                subtitle=_(
                    'Warning: this feature will use a lot of disk '
                    'space. Periodically clear the cache to '
                    'mitigate this problem'
                ),
                conf_key='random_wallpapers_names'
            )
        ]
        if DAEMON_BUILD_ENABLED:
            general_rows.append(
                PreferencesToggleRow(
                    title=_('Enable daemon'),
                    subtitle=_(
                        'Needed for slideshow mode and to detect display '
                        'changes'
                    ),
                    conf_key='enable_daemon'
                )
            )
            general_rows.append(AutostartToggleRow())
        super().__init__(
            title=_('General'), icon_name='preferences-other-symbolic',
            pref_groups=[
                MPreferencesGroup(
                    title=_('General preferences'), rows=general_rows
                ),
                MPreferencesGroup(
                    title=_('Cache and favorites'), rows=[
                        PreferencesButtonRow(
                            title=_('Clear favorites'),
                            button_label=_('Clear'),
                            onclick=self.clear_favorites,
                            button_style_class='destructive-action',
                            signal='hydrapaper_populate_wallpapers'
                        ),
                        PreferencesButtonRow(
                            title=_('Clear caches'),
                            button_label=_('Clear'),
                            onclick=self.clear_caches,
                            button_style_class='destructive-action',
                            signal='hydrapaper_populate_wallpapers'
                        )
                    ]
                )
            ]
        )

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


class AppearancePreferencesPage(MPreferencesPage):
    def __init__(self):
        super().__init__(
            title=_('Appearance'), icon_name='applications-graphics-symbolic',
            pref_groups=[
                MPreferencesGroup(
                    title=_('Appearance preferences'), rows=[
                        PreferencesToggleRow(
                            title=_('Dark mode'),
                            conf_key='dark_mode',
                            signal='dark_mode_changed'
                        ),
                        PreferencesToggleRow(
                            title=_(
                                'Use big thumbnails for the monitors previews'
                            ),
                            conf_key='big_monitor_thumbnails',
                            signal='hydrapaper_reload_monitor_thumbs'
                        ),
                        PreferencesToggleRow(
                            title=_('Show full path in folder view'),
                            conf_key='folders_popover_full_path',
                            signal='hydrapaper_set_folders_popover_labels'
                        )
                    ]
                )
            ]
        )


class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, parent_win: Optional[Gtk.Window]):
        super().__init__(default_width=640, default_height=700)
        if parent_win:
            self.set_transient_for(parent_win)
            self.set_modal(True)

        self.pages = [
            GeneralPreferencesPage(),
            AppearancePreferencesPage()
        ]
        for p in self.pages:
            self.add(p)
