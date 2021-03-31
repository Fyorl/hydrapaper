from gettext import gettext as _
from gi.repository import Gtk
from .confManager import ConfManager
from .wallpapers_folder_listbox_row import WallpapersFolderListBoxRow
from os.path import isdir


class HydraPaperWallpapersFoldersView(Gtk.Box):
    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.parent_win = window

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wallpapers_folders_view.ui'
        )

        self.container_box = self.builder.get_object(
            'wallpapersFoldersContainer'
        )
        self.listbox = self.builder.get_object('wallpapersFoldersListbox')
        self.listbox.connect(
            'row-selected', self.on_wallpapersFoldersListbox_row_selected
        )

        self.add_btn = self.builder.get_object('addWallpapersPath')
        self.add_btn.connect('clicked', self.on_addWallpapersPath_clicked)
        self.del_btn = self.builder.get_object('removeWallpapersPath')
        self.del_btn.connect('clicked', self.on_removeWallpapersPath_clicked)

        self.builder.get_object(
            'wallpaperFoldersActivateAllButton'
        ).connect(
            'clicked',
            self.on_wallpaperFoldersActivateAllButton_clicked
        )
        self.builder.get_object(
            'wallpaperFoldersDeactivateAllButton'
        ).connect(
            'clicked',
            self.on_wallpaperFoldersDeactivateAllButton_clicked
        )

        self.append(self.container_box)

        self.populate()
        self.listbox.set_sort_func(self.listbox_sort_func, None, False)
        self.show()

    def listbox_sort_func(self, row1, row2, data, notify_destroy):
        return row1.label.get_text().lower() > row2.label.get_text().lower()

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
            self.listbox.append(row)
            row.connect('row_switch_state_set', self.on_row_switch_state_set)
        self.listbox.show()

    def on_wallpapersFoldersListbox_row_selected(self, listbox, row):
        self.del_btn.set_sensitive(
            not not row and self.add_btn.get_sensitive()
        )

    def on_row_switch_state_set(self, widget, state, folder_path):
        for i, p in enumerate(self.confman.conf['wallpapers_paths']):
            if p['path'] == folder_path:
                self.confman.conf['wallpapers_paths'][i]['active'] = state
                self.confman.emit(
                    'hydrapaper_show_hide_wallpapers', 'notimportant'
                )
                self.confman.save_conf()
                break

    def on_addWallpapersPath_clicked(self, btn):
        self.fc_dialog = Gtk.FileChooserNative.new(
            _('Add wallpaper folders'),
            self.parent_win,
            Gtk.FileChooserAction.SELECT_FOLDER,
            None, None
        )
        self.fc_dialog.set_select_multiple(True)
        self.fc_dialog.set_transient_for(self.parent_win)

        def on_response(dialog, res):
            if res == Gtk.ResponseType.ACCEPT:
                for fpath in dialog.get_files():
                    fpath = fpath.get_path()
                    if isdir(fpath):
                        self.confman.conf['wallpapers_paths'].append({
                            'path': fpath,
                            'active': True
                        })
                self.confman.save_conf()
                self.populate()
                self.confman.populate_wallpapers()
                self.confman.emit(
                    'hydrapaper_populate_wallpapers', 'notimportant'
                )
            dialog.destroy()
            self.fc_dialog = None

        self.fc_dialog.connect('response', on_response)
        self.fc_dialog.show()

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

    def set_all_enabled(self, state):
        # This is a nice hack
        # The obvious thing to do would be to cycle the listbox rows and toggle
        # all of them one by one. This is possible but not optimal since every
        # time a row switch is toggled, the config file is saved meaning file
        # system access meaning the UI freezes for about half a second. Instead
        # I just edit the conf to set the path active state there, the call
        # populate to empty the listbox and re-populate it with the new values
        # directly from the config, finally I just save once. This works nicely
        for i, wp_path in enumerate(self.confman.conf['wallpapers_paths']):
            self.confman.conf['wallpapers_paths'][i]['active'] = state
        self.populate()
        self.confman.emit('hydrapaper_show_hide_wallpapers', 'notimportant')
        self.confman.save_conf()

    def on_wallpaperFoldersActivateAllButton_clicked(self, btn):
        self.set_all_enabled(True)

    def on_wallpaperFoldersDeactivateAllButton_clicked(self, btn):
        self.set_all_enabled(False)
