from gi.repository import Gtk
import pathlib

class HydraPaperWallpapersFlowbox(Gtk.Bin):
    def __init__(self, is_favorites=False, **kwargs):
        super().__init__(**kwargs)
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
        self.longpress.set_touch_only(False)
        self.longpress.connect(
            'pressed',
            self.on_wallpapersFlowbox_rightclick_or_longpress
        )

    def on_wallpapersFlowbox_child_activated(self, flowbox, child):
        pass

    def on_wallpapersFlowbox_rightclick_or_longpress(self, gesture_or_event, x, y):
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
