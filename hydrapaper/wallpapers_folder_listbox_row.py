from gi.repository import Gtk, GObject
from .confManager import ConfManager


class WallpapersFolderListBoxRow(Gtk.ListBoxRow):
    __gsignals__ = {
        'row_switch_state_set': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (bool, str)
        )
    }

    def __init__(self, folder_path, folder_active):
        super().__init__()

        self.confman = ConfManager()
        self.folder_path = folder_path

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.label = Gtk.Label()
        self.switch = Gtk.CheckButton()

        self.set_label_text()
        self.label.set_margin_start(12)
        self.label.set_margin_end(6)
        self.label.set_halign(Gtk.Align.START)

        self.switch.set_active(folder_active)
        self.switch.set_margin_start(6)
        self.switch.set_margin_end(12)

        self.box.append(self.label)
        self.label.set_hexpand(True)
        self.box.append(self.switch)
        self.box.set_margin_top(6)
        self.box.set_margin_bottom(6)

        self.value = folder_path

        self.set_child(self.box)
        self.switch.connect('toggled', self.on_switch_state_set)
        self.confman.connect(
            'hydrapaper_set_folders_popover_labels',
            self.set_label_text
        )

    def on_switch_state_set(self, switch):
        state = self.switch.get_active()
        self.emit('row_switch_state_set', state, self.value)

    def set_label_text(self, *args):
        text = self.folder_path
        if not self.confman.conf['folders_popover_full_path']:
            text = text.split('/')[-1]
        self.label.set_text(text)
