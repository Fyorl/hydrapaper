from gi.repository import Gtk, Gdk
from .confManager import ConfManager
from .wallpapers_folder_listbox_row import WallpapersFolderListBoxRow
from os.path import isdir

class HydraPaperWallpapersFoldersView(Gtk.Bin):
    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wallpapers_folders_view.glade'
        )

        self.container_box = self.builder.get_object('wallpapersFoldersContainer')
        self.listbox = self.builder.get_object('wallpapersFoldersListbox')

        self.add_btn = self.builder.get_object('addWallpapersPath')
        self.del_btn = self.builder.get_object('removeWallpapersPath')

        self.add(self.container_box)

        self.builder.connect_signals(self)
        self.populate()

        self.dialog_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/choose_folder_dialog.glade'
        )
        self.file_chooser_dialog = self.dialog_builder.get_object(
            'addFolderFileChooserDialog'
        )
        self.file_chooser_dialog.set_skip_taskbar_hint(True)
        self.file_chooser_dialog.set_skip_pager_hint(True)
        self.file_chooser_dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.file_chooser_dialog.set_modal(True)
        self.file_chooser_dialog.set_transient_for(window)
        # self.file_chooser_dialog.set_attached_to(window)
        self.file_chooser_dialog_revealer = self.dialog_builder.get_object(
            'infoRevealer'
        )
        self.dialog_builder.connect_signals(self)
        self.show_all()

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

    def on_row_switch_state_set(self, widget, state, folder_path):
        for i, p in enumerate(self.confman.conf['wallpapers_paths']):
            if p['path'] == folder_path:
                self.confman.conf['wallpapers_paths'][i]['active'] = state
                self.confman.emit('hydrapaper_show_hide_wallpapers', 'notimportant')
                self.confman.save_conf()
                break

    def on_addWallpapersPath_clicked(self, btn):
        self.file_chooser_dialog.present()

    def on_addFolderFileChooserDialogCancelButton_clicked(self, btn):
        self.file_chooser_dialog.hide()
        self.file_chooser_dialog_revealer.set_reveal_child(False)

    def on_infoRevealerCloseBtn_clicked(self, btn):
        self.file_chooser_dialog_revealer.set_reveal_child(False)

    def on_addFolderFileChooserDialogOpenButton_clicked(self, btn):
        fpath = self.file_chooser_dialog.get_filename()
        if not isdir(fpath):
            return
        if fpath in [wp['path'] for wp in self.confman.conf['wallpapers_paths']]:
            self.file_chooser_dialog_revealer.set_reveal_child(True)
            return
        self.file_chooser_dialog.hide()
        self.file_chooser_dialog_revealer.set_reveal_child(False)
        self.confman.conf['wallpapers_paths'].append({
            'path': fpath,
            'active': True
        })
        self.confman.save_conf()
        self.populate()
        self.confman.populate_wallpapers()
        self.confman.emit('hydrapaper_populate_wallpapers', 'notimportant')

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
        
