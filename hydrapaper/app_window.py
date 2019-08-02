from gi.repository import Gtk , Handy
from .wnck_win_controller import change_minimize_state
from .confManager import ConfManager
from .main_stack import HydraPapaerMainStack
from .monitors_flowbox import HydraPaperMonitorsFlowbox
from .apply_wallpapers import apply_wallpapers
from .headerbar import HydraPaperHeaderbar

class HydraPaperAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title('HydraPaper')
        self.set_icon_name('org.gabmus.hydrapaper')
        self.container_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.bottom_bar = Handy.ViewSwitcherBar()
        self.headerbar = HydraPaperHeaderbar(self, self.apply_handler)
        self.stack_switcher = self.headerbar.stack_switcher
        self.folders_view = self.headerbar.folders_view
        self.main_stack = HydraPapaerMainStack()
        self.stack_switcher.set_stack(self.main_stack)
        self.bottom_bar.set_stack(self.main_stack)
        self.monitors_flowbox = HydraPaperMonitorsFlowbox()

        self.container_box.pack_start(self.monitors_flowbox, False, False, 6)
        self.container_box.pack_start(self.main_stack, True, True, 0)
        self.container_box.pack_start(self.bottom_bar, False, False, 0)
        self.add(self.container_box)
        self.set_titlebar(self.headerbar)
        # Why this -52?
        # because every time a new value is saved, for some reason
        # it's the actual value +52 out of nowhere
        # this makes the window ACTUALLY preserve its old size
        self.resize(
            self.confman.conf['windowsize']['width']-52,
            self.confman.conf['windowsize']['height']-52
        )
        self.size_allocation = self.get_allocation()
        self.connect('size-allocate', self.update_size_allocation)

        self.menu_popover = self.headerbar.menu_popover
        self.menu_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/menu.xml'
        )
        self.menu = self.menu_builder.get_object('generalMenu')
        self.menu_popover.bind_model(self.menu)

        # accel_group is for keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        shortcuts_l = [
            {
                'combo': '<Control>q',
                'cb': self.emit_destroy
            }
        ]
        for s in shortcuts_l:
            self.add_accelerator(s['combo'], s['cb'])

    def add_accelerator(self, shortcut, callback):
        if shortcut:
            key, mod = Gtk.accelerator_parse(shortcut)
            self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, callback)

    def emit_destroy(self, *args):
        self.emit('destroy')

    def update_size_allocation(self, *args):
        self.size_allocation = self.get_allocation()

    def show_all(self, **kwargs):
        super().show_all(**kwargs)
        self.main_stack.main_flowbox.show_hide_wallpapers()

    def apply_handler(self, btn, lockscreen = False):
        apply_wallpapers(
            monitors = self.monitors_flowbox.monitors,
            widgets_to_freeze = [
                btn,
                self.folders_view
            ],
            lockscreen = lockscreen
        )
        self.monitors_flowbox.dump_to_config()

    def on_destroy(self, *args):
        change_minimize_state(state = False)
        self.confman.conf['windowsize'] = {
            'width': self.size_allocation.width,
            'height': self.size_allocation.height
        }
        self.confman.save_conf()
