from gettext import gettext as _
from gi.repository import Gtk, GLib
import os
from PIL import Image
from hashlib import sha256
from .confManager import ConfManager
from pathlib import Path
from threading import Thread


class WallpaperItemPopover(Gtk.Popover):
    def __init__(self, wp_path, parent_w, **kwargs):
        super().__init__(**kwargs)
        self.wp_path = wp_path
        self.parent_w = parent_w
        self.set_parent(self.parent_w)
        # self.set_pointing_to(self.parent_w.get_allocation())
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_autohide(True)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/wallpaper_flowbox_item_popover.glade'
        )
        self.content = self.builder.get_object('flowbox_item_popover_content')
        self.set_child(self.content)

        self.favorite_btn = self.builder.get_object('favoriteBtn')
        self.favorite_btn.connect('clicked', self.on_favoriteBtn_clicked)
        self.wallpaper_path_entry = self.builder.get_object(
            'wallpaperPathEntry'
        )
        self.wallpaper_name_label = self.builder.get_object(
            'wallpaperNameLabel'
        )

    def popup(self, *args):
        if (
                self.parent_w.get_parent().get_parent().get_parent(
                    ).get_parent().is_favorites or
                self.parent_w.is_fav
        ):
            self.favorite_btn.set_label(_('Remove favorite'))
        else:
            self.favorite_btn.set_label(_('Add favorite'))
        self.wallpaper_path_entry.set_text(self.wp_path)
        self.wallpaper_name_label.set_text(Path(self.wp_path).name)
        super().popup(*args)

    def on_favoriteBtn_clicked(self, btn):
        self.parent_w.set_fav(not self.parent_w.is_fav)
        self.parent_w.confman.emit('hydrapaper_populate_wallpapers', '')
        self.popdown()


class WallpaperBox(Gtk.FlowBoxChild):

    def __init__(self, wp_path, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.set_size_request(250, 250)

        self.wallpaper_path = wp_path
        self.popover = WallpaperItemPopover(self.wallpaper_path, self)
        self.pathlib_path = Path(wp_path)
        self.cache_path = '{0}/{1}.png'.format(
            self.confman.thumbs_cache_path,
            sha256(
                f'HydraPaperThumb{self.wallpaper_path}'.encode()
            ).hexdigest()
        )
        self.is_fav = False
        self.container_box = Gtk.Overlay()
        self.container_box.set_halign(Gtk.Align.CENTER)
        self.container_box.set_valign(Gtk.Align.CENTER)
        self.container_box.set_size_request(250, 250)
        self.wp_image = Gtk.Picture()
        self.wp_image.set_size_request(250, -1)
        self.wp_image.set_can_shrink(False)
        self.heart_icon = Gtk.Image.new_from_resource(
            '/org/gabmus/hydrapaper/icons/favorite-badge.svg'
        )
        self.heart_icon.set_icon_size(Gtk.IconSize.LARGE)
        self.heart_icon.hide()
        self.heart_icon.set_halign(Gtk.Align.START)
        self.heart_icon.set_valign(Gtk.Align.CENTER)
        self.heart_icon.set_margin_start(12)
        self.container_box.add_overlay(self.wp_image)
        self.container_box.wallpaper_path = wp_path

        self.container_box.add_overlay(self.heart_icon)
        self.heart_icon.hide()

        self.set_child(self.container_box)
        self.set_wallpaper_thumb()
        self.set_fav(self.wallpaper_path in self.confman.conf['favorites'])

        self.click_gesture = Gtk.GestureClick.new()
        self.click_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.click_gesture.set_button(3)
        self.click_gesture.connect(
            'released', self.on_rightclick
        )
        self.add_controller(self.click_gesture)

        self.longpress = Gtk.GestureLongPress.new()
        self.longpress.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.longpress.set_touch_only(False)
        self.longpress.connect(
            'pressed',
            self.on_rightclick
        )
        self.add_controller(self.longpress)

    def on_rightclick(self, *args):
        self.get_parent().select_child(self)
        self.confman.emit(
            'hydrapaper_flowbox_wallpaper_selected',
            self.wallpaper_path
        )
        self.popover.popup()

    def set_wallpaper_thumb(self):

        def af():
            self.make_wallpaper_thumb(self.cache_path)
            GLib.idle_add(cb)

        def cb():
            self.wp_image.set_filename(self.cache_path)
            self.wp_image.show()

        if os.path.isfile(self.cache_path):
            cb()
        else:
            Thread(target=af).start()

    def set_fav(self, fav: bool):
        self.is_fav = fav
        if self.is_fav:
            self.heart_icon.show()
            if self.wallpaper_path not in self.confman.conf['favorites']:
                self.confman.conf['favorites'].append(self.wallpaper_path)
        else:
            self.heart_icon.hide()
            if self.wallpaper_path in self.confman.conf['favorites']:
                self.confman.conf['favorites'].pop(
                    self.confman.conf['favorites'].index(self.wallpaper_path)
                )
        self.confman.save_conf()

    def make_wallpaper_thumb(self, wp_path):
        try:
            thumb = Image.open(self.wallpaper_path)
            thumb.thumbnail((250, 250), Image.ANTIALIAS)
            thumb.save(self.cache_path, 'PNG')
        except IOError:
            print(
                _('ERROR: cannot create thumbnail for file'),
                self.wallpaper_path
            )
        return self.cache_path
