from gi.repository import Gtk, Handy
from .confManager import ConfManager
from .main_stack import HydraPapaerMainStack
from .monitors_flowbox import HydraPaperMonitorsFlowbox
from .apply_wallpapers import apply_wallpapers
from .headerbar import HydraPaperHeaderbar


class HydraPaperAppWindow(Handy.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title('HydraPaper')
        self.set_icon_name('org.gabmus.hydrapaper')
        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.bottom_bar = Handy.ViewSwitcherBar()
        self.headerbar = HydraPaperHeaderbar(self, self.apply_handler)
        self.stack_switcher = self.headerbar.stack_switcher
        self.folders_view = self.headerbar.folders_view
        self.main_stack = HydraPapaerMainStack()
        self.stack_switcher.set_stack(self.main_stack)
        self.bottom_bar.set_stack(self.main_stack)
        self.monitors_flowbox = HydraPaperMonitorsFlowbox()
        # self.separator = Gtk.Separator()
        # self.separator.get_style_context().add_class('sidebar')

        self.window_handle = Gtk.WindowHandle()
        self.window_handle.set_child(self.headerbar)
        self.container_box.append(self.window_handle)
        self.window_handle.set_vexpand(False)
        self.container_box.append(self.monitors_flowbox)
        # self.container_box.pack_start(self.separator, False, False, 0)
        self.container_box.append(self.main_stack)
        self.main_stack.set_vexpand(True)
        self.container_box.append(self.bottom_bar)
        self.set_child(self.container_box)
        self.resize(
            self.confman.conf['windowsize']['width'],
            self.confman.conf['windowsize']['height']
        )

        self.menu_popover = self.headerbar.menu_popover
        self.menu_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/menu.xml'
        )
        self.menu = self.menu_builder.get_object('generalMenu')
        self.menu_popover.set_menu_model(self.menu)

        shortcuts_l = [
            {
                'combo': 'F10',
                'cb': self.toggle_menu
            }
        ]
        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)
        for s in shortcuts_l:
            self.add_accelerator(s['combo'], s['cb'])
        self.add_controller(self.shortcut_controller)

    def add_accelerator(self, shortcut, callback):
        if shortcut:
            # res is bool, don't know what it is
            res, key, mod = Gtk.accelerator_parse(shortcut)
            trigger = Gtk.KeyvalTrigger.new(key, mod)
            cb = Gtk.CallbackAction.new(callback)
            shortcut = Gtk.Shortcut.new(trigger, cb)
            self.shortcut_controller.add_shortcut(shortcut)

    def toggle_menu(self, *args):
        popover = self.headerbar.menu_button.get_popover()
        if popover.get_visible():
            popover.popdown()
        else:
            popover.popup()

    def emit_destroy(self, *args):
        self.emit('destroy')

    def show(self, **kwargs):
        super().show(**kwargs)
        self.main_stack.main_flowbox.show_hide_wallpapers()

    def apply_handler(self, btn, lockscreen=False):
        apply_wallpapers(
            monitors=self.monitors_flowbox.get_monitors(),
            widgets_to_freeze=[
                btn,
                self.folders_view
            ],
            lockscreen=lockscreen
        )
        self.monitors_flowbox.dump_to_config()

    def on_destroy(self, *args):
        alloc = self.get_allocation()
        self.confman.conf['windowsize'] = {
            'width': alloc.width,
            'height': alloc.height
        }
        self.confman.save_conf()
