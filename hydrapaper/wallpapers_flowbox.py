from gi.repository import Gtk
from .confManager import ConfManager
from .wallpaper_flowbox_item import WallpaperBox
import pathlib

class HydraPaperWallpapersFlowbox(Gtk.Bin):
    def __init__(self, is_favorites=False, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.is_favorites = is_favorites
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wallpapers_flowbox.glade'
        )

        self.flowbox = self.builder.get_object('wallpapersFlowbox')
        self.popover = self.builder.get_object('flowboxItemPopover')
        self.favorite_btn = self.builder.get_object('favoriteBtn')
        self.wallpaper_path_entry = self.builder.get_object(
            'wallpaperPathEntry'
        )
        self.wallpaper_name_label = self.builder.get_object(
            'wallpaperNameLabel'
        )
        self.scrolled_win = self.builder.get_object('scrolledWin')

        self.add(self.scrolled_win)

        self.builder.connect_signals(self)
        self.child_at_pos = None

        self.longpress = Gtk.GestureLongPress.new(self.flowbox)
        self.longpress.set_propagation_phase(Gtk.PropagationPhase.TARGET)
        self.longpress.set_touch_only(False)
        self.longpress.connect(
            'pressed',
            self.on_wallpapersFlowbox_rightclick_or_longpress,
            self.flowbox
        )
        self.flowbox.set_activate_on_single_click(
            self.confman.conf['selection_mode'] == 'single'
        )
        self.confman.connect(
            'hydrapaper_flowbox_selection_mode_changed',
            self.change_selection_mode
        )
        self.confman.connect(
            'hydrapaper_populate_wallpapers',
            self.populate
        )
        self.confman.connect(
            'hydrapaper_show_hide_wallpapers',
            self.show_hide_wallpapers
        )
        self.populate()

    def change_selection_mode(self, *args):
        self.flowbox.set_activate_on_single_click(
            self.confman.conf['selection_mode'] == 'single'
        )

    def populate(self, *args):
        # this while empties self before filling
        while True:
            c = self.flowbox.get_child_at_index(0)
            if c:
                self.flowbox.remove(c)
                c.destroy()
            else:
                break
        if self.is_favorites:
            for wp in self.confman.wallpapers:
                if wp in self.confman.conf['favorites']:
                    self.flowbox.add(WallpaperBox(wp))
        else:
            for wp in self.confman.wallpapers:
                self.flowbox.add(WallpaperBox(wp))
        self.show_all()
        self.show_hide_wallpapers()

    def show_hide_wallpapers(self, *args):
        if self.is_favorites:
            return
        self.show_all()
        for p in self.confman.conf['wallpapers_paths']:
            if not p['active']:
                for c in self.flowbox.get_children():
                    if p['path'] in c.wallpaper_path:
                        c.hide()
        if not self.confman.conf['favorites_in_mainview']:
            for c in self.flowbox.get_children():
                if c.wallpaper_path in self.confman.conf['favorites']:
                    c.hide()

    def on_wallpapersFlowbox_child_activated(self, flowbox, child):
        self.confman.emit(
            'hydrapaper_flowbox_wallpaper_selected',
            child.wallpaper_path
        )

    def on_wallpapersFlowbox_rightclick_or_longpress(self, gesture_or_event, x, y, *args):
        self.child_at_pos = self.flowbox.get_child_at_pos(x,y)
        if not self.child_at_pos:
            return
        self.popover.set_relative_to(self.child_at_pos)
        self.flowbox.select_child(self.child_at_pos)
        if self.is_favorites or self.child_at_pos.is_fav:
            self.favorite_btn.set_label('💔 Remove favorite')
        else:
            self.favorite_btn.set_label('❤️ Add favorite')
        wp_path = self.child_at_pos.get_child().wallpaper_path
        self.wallpaper_path_entry.set_text(wp_path)
        self.wallpaper_name_label.set_text(pathlib.Path(wp_path).name)
        self.on_wallpapersFlowbox_child_activated(self.flowbox, self.child_at_pos)
        self.popover.popup()

    def on_wallpapersFlowbox_button_release_event(self, flowbox, event):
        if event.button == 3: # 3 is the right mouse button
            self.on_wallpapersFlowbox_rightclick_or_longpress(
                event,
                event.x,
                event.y
            )

    def on_favoriteBtn_clicked(self, btn):
        child = self.flowbox.get_selected_children()[0]
        if not child:
            return
        child.set_fav(not child.is_fav)
        self.confman.emit('hydrapaper_populate_wallpapers', 'notimportant')
        self.popover.popdown()
