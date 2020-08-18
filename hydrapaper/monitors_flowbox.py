from gi.repository import Gtk, GdkPixbuf
from .confManager import ConfManager
from .monitor_parser import build_monitors_autodetect, Monitor
from .is_image import is_image
from .wallpaper_merger import get_combined_resolution
from hashlib import sha256
from os.path import isfile
from gettext import gettext as _


WALLPAPER_MODE_VALUES = [
    'zoom', 'fit_black', 'fit_blur', 'center_black', 'center_blur'
]


class WallpaperModePopover(Gtk.PopoverMenu):
    def __init__(self, relative_to, **kwargs):
        super().__init__(**kwargs)
        self.set_modal(True)
        self.set_relative_to(relative_to)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wp_mode_popover_menu.glade'
        )
        self.radio_zoom = self.builder.get_object('radio_zoom')
        self.radio_fit_black = self.builder.get_object('radio_fit_black')
        self.radio_fit_blur = self.builder.get_object('radio_fit_blur')
        self.radio_center_black = self.builder.get_object('radio_center_black')
        self.radio_center_blur = self.builder.get_object('radio_center_blur')
        self.radios_dict = {
            'zoom': self.radio_zoom,
            'fit_black': self.radio_fit_black,
            'fit_blur': self.radio_fit_blur,
            'center_black': self.radio_center_black,
            'center_blur': self.radio_center_blur
        }
        self.radios = list(self.radios_dict.values())
        self.add(self.builder.get_object('menu_box'))


class HydraPaperMonitorsFlowboxItem(Gtk.FlowBoxChild):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.monitor = monitor

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/monitors_flowbox_item.glade'
        )

        self.box = self.builder.get_object('main_box')
        self.label = self.builder.get_object('label')
        self.label.set_text(self.monitor.name)
        self.overlay = self.builder.get_object('overlay')
        self.wp_mode_btn = self.builder.get_object('wp_mode_btn')
        self.wp_mode_popover = WallpaperModePopover(self.wp_mode_btn)
        self.wp_mode_btn.connect(
            'clicked',
            lambda *args: self.wp_mode_popover.popup()
        )
        self.image = self.builder.get_object('wp_preview')
        self.add(self.box)

        for radio, value in zip(
                self.wp_mode_popover.radios,
                WALLPAPER_MODE_VALUES
        ):
            radio.connect(
                'toggled',
                self.on_wp_mode_changed,
                value
            )

        self.set_picture()
        self.show_all()

    def on_wp_mode_changed(self, radio, value):
        # check that the signal is sent from a radio that has been turned on
        # and not turned off by another radio
        if radio.get_active():
            self.monitor.mode = value

    def set_picture(self, n_wp=None):
        wp_size = 256 if self.confman.conf['big_monitor_thumbnails'] else 64
        if n_wp and is_image(n_wp):
            self.monitor.wallpaper = n_wp
        if self.monitor.wallpaper and is_image(self.monitor.wallpaper):
            thumb_path = '{0}/{1}.png'.format(
                self.confman.thumbs_cache_path,
                sha256(
                    f'HydraPaperThumb{self.monitor.wallpaper}'.encode()
                ).hexdigest()
            )
            if not isfile(thumb_path):
                thumb_path = self.monitor.wallpaper
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                thumb_path, wp_size, wp_size, True
            )
            self.image.set_from_pixbuf(pixbuf)
        else:
            self.image.set_from_icon_name(
                'image-x-generic-symbolic',
                Gtk.IconSize.DIALOG
            )
        self.wp_mode_popover.radios_dict[self.monitor.mode].set_active(True)


class HydraPaperMonitorsFlowbox(Gtk.FlowBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.monitors = build_monitors_autodetect()
        self.spanned_monitor = Monitor(
            *get_combined_resolution(self.monitors),
            1,
            0, 0,
            0,
            _('Combined spanned monitor'),
            'zoom',
            True,
            True
        )

        self.set_min_children_per_line(1)
        self.set_max_children_per_line(len(self.monitors))
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)
        self.set_homogeneous(False)
        self.set_vexpand(False)
        self.set_activate_on_single_click(
            self.confman.conf['selection_mode']
        )
        self.confman.connect(
            'hydrapaper_flowbox_wallpaper_selected',
            self.change_selected_wp
        )
        self.confman.connect(
            'hydrapaper_reload_monitor_thumbs',
            self.reload_children_pictures
        )
        self.confman.connect(
            'hydrapaper_spanned_mode_changed',
            self.populate
        )
        self.populate()

    def populate(self, *args):
        while True:
            item = self.get_child_at_index(0)
            if item is not None:
                self.remove(item)
            else:
                break
        if self.confman.conf['spanned_mode']:
            self.add(
                HydraPaperMonitorsFlowboxItem(
                    self.spanned_monitor
                )
            )
            self.set_max_children_per_line(1)
        else:
            self.load_from_config()
            for m in self.monitors:
                self.add(
                    HydraPaperMonitorsFlowboxItem(m)
                )
            self.set_max_children_per_line(len(self.monitors))
        self.select_child(self.get_children()[0])

    def get_monitors(self):
        return (
            [self.spanned_monitor]
            if self.confman.conf['spanned_mode']
            else self.monitors
        )

    def reload_children_pictures(self, *args):
        for c in self.get_children():
            c.set_picture()

    def load_from_config(self):
        for m in self.monitors:
            if m.name in self.confman.conf['monitors'].keys():
                m.wallpaper = self.confman.conf['monitors'][m.name]['wallpaper']
                m.mode = self.confman.conf['monitors'][m.name]['mode']

    def dump_to_config(self):
        n_monitors = {}
        for m in self.monitors:
            n_monitors[m.name] = {
                'wallpaper': m.wallpaper,
                'mode': m.mode
            }
        self.confman.conf['monitors'] = n_monitors
        self.confman.save_conf()

    def change_selected_wp(self, signaler, n_wp, *args):
        selected_monitor_widget = self.get_selected_children()[0]
        if not selected_monitor_widget:
            return
        for i, m in enumerate(self.monitors):
            if m.name == selected_monitor_widget.monitor.name:
                self.monitors[i].wallpaper = n_wp
                break
        selected_monitor_widget.set_picture(n_wp)
