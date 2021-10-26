from gi.repository import Gtk, Adw
from .confManager import ConfManager
from .main_stack import HydraPapaerMainStack
from .monitors_flowbox import HydraPaperMonitorsFlowbox
from .apply_wallpapers import apply_wallpapers
from .headerbar import HydraPaperHeaderbar
from .base_app import BaseWindow, AppShortcut


class HydraPaperAppWindow(BaseWindow):
    def __init__(self):
        super().__init__(
            app_name='HydraPaper',
            icon_name='org.gabmus.hydrapaper',
            shortcuts=[AppShortcut(
                'F10', lambda *args: self.headerbar.menu_button.popup()
            )]
        )
        self.confman = ConfManager()

        self.bottom_bar = Adw.ViewSwitcherBar()
        self.headerbar = HydraPaperHeaderbar(self, self.apply_handler)
        self.stack_switcher = self.headerbar.stack_switcher
        self.folders_view = self.headerbar.folders_view
        self.main_stack = HydraPapaerMainStack()
        self.stack_switcher.set_stack(self.main_stack)
        self.bottom_bar.set_stack(self.main_stack)
        self.monitors_flowbox = HydraPaperMonitorsFlowbox()

        self.window_handle = Gtk.WindowHandle(vexpand=False)
        self.window_handle.set_child(self.headerbar)
        self.append(self.window_handle)
        self.append(self.monitors_flowbox)
        self.append(self.main_stack)
        self.append(self.bottom_bar)

        self.confman.connect(
            'dark_mode_changed',
            lambda *args: self.set_dark_mode(self.confman.conf['dark_mode'])
        )
        self.set_dark_mode(self.confman.conf['dark_mode'])

    def present(self):
        super().present()
        self.set_default_size(
            self.confman.conf['windowsize']['width'],
            self.confman.conf['windowsize']['height']
        )

    def emit_destroy(self, *args):
        self.emit('destroy')

    def show(self, **kwargs):
        super().show(**kwargs)
        self.main_stack.main_flowbox.show_hide_wallpapers()

    def apply_handler(self, btn):
        apply_wallpapers(
            monitors=self.monitors_flowbox.get_monitors(),
            widgets_to_freeze=[
                btn,
                self.folders_view
            ]
        )
        self.monitors_flowbox.dump_to_config()

    def on_destroy(self, *args):
        self.confman.conf['windowsize'] = {
            'width': self.get_width(),
            'height': self.get_height()
        }
        self.confman.save_conf()
