from gi.repository import Gtk
from .confManager import ConfManager
from .wnck_win_controller import change_minimize_state
from .wallpapers_folders_view import HydraPaperWallpapersFoldersView
from .main_stack import HydraPapaerMainStack
from .monitors_flowbox import HydraPaperMonitorsFlowbox

class HydraPaperAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.resize(
            self.confman.conf['windowsize']['width'],
            self.confman.conf['windowsize']['height']
        )

        self.set_title('HydraPaper')
        self.set_icon_name('org.gabmus.hydrapaper')
        self.container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        self.headerbar_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/headerbar.glade'
        )
        self.headerbar = self.headerbar_builder.get_object('headerbar')
        self.menu_popover = self.headerbar_builder.get_object('menuPopover')
        self.wallpapers_folders_popover = self.headerbar_builder.get_object(
            'wallpapersFoldersPopover'
        )
        self.folders_view = HydraPaperWallpapersFoldersView()
        self.wallpapers_folders_popover.add(self.folders_view)
        self.apply_spinner = self.headerbar_builder.get_object('applySpinner')
        self.stack_switcher = self.headerbar_builder.get_object(
            'mainStackSwitcher'
        )
        self.main_stack = HydraPapaerMainStack()
        self.stack_switcher.set_stack(self.main_stack)
        self.monitors_flowbox = HydraPaperMonitorsFlowbox()

        self.container.pack_start(self.monitors_flowbox, False, False, 6)
        self.container.pack_start(self.main_stack, True, True, 6)
        self.add(self.container)
        self.headerbar_builder.connect_signals(self)

    def on_applyButton_clicked(self, btn):
        pass

    def on_menuBtn_clicked(self, btn):
        self.menu_popover.popup()

    def on_wallpapersFoldersBtn_clicked(self, btn):
        self.wallpapers_folders_popover.popup()

    def on_lowerAllOtherWindowsToggle_toggled(self, toggle):
        change_minimize_state(toggle = toggle)

    def destroy(self, *args):
        change_minimize_state(state = False)
        allocation = self.get_allocation()
        self.confman.conf['windowsize'] = {
            'width': allocation.width,
            'height': allocation.height
        }
        self.confman.save_conf()
        self.emit('destroy')
