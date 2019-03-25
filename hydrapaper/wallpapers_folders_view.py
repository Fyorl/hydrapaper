from gi.repository import Gtk
from .confManager import ConfManager
from .wallpapers_folder_listbox_row import WallpapersFolderListBoxRow

class HydraPaperWallpapersFoldersView(Gtk.Bin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wallpapers_folders_view.glade'
        )

        self.container = self.builder.get_object('wallpapersFoldersContainer')
        self.listbox = self.builder.get_object('wallpapersFoldersListbox')

        self.add_btn = self.builder.get_object('addWallpapersPath')
        self.del_btn = self.builder.get_object('removeWallpapersPath')

        self.add(self.container)

        self.builder.connect_signals(self)
        self.populate()

    def populate(self):
        while True:
            row = self.listbox.get_row_at_index(0)
            if row:
                self.listbox.remove(row)
            else:
                break
        for folder in self.confman.conf['wallpapers_paths']:
            row = WallpapersFolderListBoxRow(
                folder['path'],
                folder['active']
            )
            self.listbox.add(row)
            row.connect('row_switch_state_set', self.on_row_switch_state_set)
        self.listbox.show_all()

    def on_wallpapersFoldersListbox_row_selected(self, listbox, row):
        self.del_btn.set_sensitive(
            not not row and self.add_btn.get_sensitive()
        )

    def on_row_switch_state_set(self, state, folder_path):
        pass

    def on_addWallpapersPath_clicked(self, btn):
        pass

    def on_removeWallpapersPath_clicked(self, btn):
        row = self.listbox.get_selected_row()
        if not row:
            return
        if not row.value:
            return
        c_paths = self.confman.conf['wallpapers_paths']
        for i, p in enumerate(c_paths):
            if p['path'] == row.value:
                c_paths.pop(i)
                self.confman.conf['wallpapers_paths'] = c_paths
                self.confman.populate_wallpapers()
                break
        for i, fav in enumerate(self.confman.conf['favorites']):
            if row.value in fav:
                self.confman.conf['favorites'].pop(i)
        self.confman.save_conf()
        self.populate()
        
