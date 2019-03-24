from gi.repository import Gtk, GdkPixbuf
from .confManager import ConfManager
from .monitor_parser import build_monitors_from_gdk
from .is_image import is_image
from hashlib import sha256
from os.path import isfile

class HydraPaperMonitorsFlowboxItem(Gtk.FlowBoxChild):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.monitor = monitor

        self.box = Gtk.Box(
            orientation = Gtk.Orientation.VERTICAL
        )
        self.label = Gtk.Label()
        self.label.set_text(self.monitor.name),
        self.image = Gtk.Image()
        self.box.pack_start(self.image, False, False, 0)
        self.box.pack_start(self.label, False, False, 0)
        self.box.set_margin_left(24)
        self.box.set_margin_right(24)
        self.add(self.box)
        self.set_picture()

    def set_picture(self, n_wp=None):
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
                thumb_path, 64, 64, True
            )
            self.image.set_from_pixbuf(pixbuf)
        else:
            image.set_from_icon_name(
                'image-x-generic-symbolic',
                Gtk.IconSize.DIALOG
            )

class HydraPaperMonitorsFlowbox(Gtk.FlowBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.monitors = build_monitors_from_gdk()

        self.set_min_children_per_line(4)
        self.set_max_children_per_line(7)
        self.set_activate_on_single_click(
            self.confman.conf['selection_mode']
        )

    def populate(self):
        self.load_from_config()
        for m in self.monitors:
            self.add(
                HydraPaperMonitorsFlowboxItem(m)
            )

    def load_from_config(self):
        for m in self.monitors:
            if m.name in self.confman.conf['monitors'].keys():
                m.wallpaper = self.confman.conf['monitors'][m.name]

    def dump_to_config(self):
        n_monitors = {}
        for m in self.monitors:
            n_monitors[m.name] = m.wallpaper
        self.confman.conf['monitors'] = n_monitors
        self.confman.save_conf()

    def change_selected_wp(self, n_wp):
        selected_monitor_widget = self.get_selected_children()[0]
        if not selected_monitor_widget:
            return
        for i, m in enumerate(self.monitors):
            if m.name == selected_monitor_widget.monitor.name:
                self.monitors[i].wallpaper = n_wp
                break
        selected_monitor_widget.set_picture(n_wp)
