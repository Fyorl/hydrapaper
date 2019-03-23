from gi.repository import Gtk, GdkPixbuf
from .confManager import ConfManager
from .monitor_parser import build_monitors_from_gdk
from .is_image import is_image

class HydraPaperMonitorsFlowboxItem(Gtk.FlowBoxChild):
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
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

    def set_picture(self):
        if self.monitor.wallpaper and is_image(self.monitor.wallpaper):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.monitor.wallpaper, 64, 64, True
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
        for m in self.monitors:
            self.add(
                HydraPaperMonitorsFlowboxItem(m)
            )
