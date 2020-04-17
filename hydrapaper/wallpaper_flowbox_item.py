from gettext import gettext as _
from gi.repository import Gtk
import os
from . import threading_helper as ThreadingHelper
from PIL import Image
from hashlib import sha256
from .confManager import ConfManager
from pathlib import Path


class WallpaperBox(Gtk.FlowBoxChild):

    def __init__(self, wp_path, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        self.wallpaper_path = wp_path
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
        self.wp_image = Gtk.Image.new_from_icon_name(
            'image-x-generic', Gtk.IconSize.DIALOG)
        self.heart_icon = Gtk.Image.new_from_resource(
            '/org/gabmus/hydrapaper/icons/favorite-badge.svg')
        self.heart_icon.set_no_show_all(True)
        self.heart_icon.set_halign(Gtk.Align.END)
        self.heart_icon.set_valign(Gtk.Align.END)
        # self.heart_icon.set_margin_bottom(6)
        # self.heart_icon.set_margin_right(6)
        self.container_box.add(self.wp_image)
        self.container_box.set_margin_left(12)
        self.container_box.set_margin_right(12)
        self.container_box.wallpaper_path = wp_path

        self.container_box.add_overlay(self.heart_icon)
        self.heart_icon.hide()

        self.add(self.container_box)
        self.set_wallpaper_thumb()
        self.set_fav(self.wallpaper_path in self.confman.conf['favorites'])

    def set_wallpaper_thumb(self):
        if not os.path.isfile(self.cache_path):
            mkthumb_thread = ThreadingHelper.do_async(
                self.make_wallpaper_thumb,
                (self.wallpaper_path,)
            )
            ThreadingHelper.wait_for_thread(mkthumb_thread)
        self.wp_image.set_from_file(self.cache_path)
        self.wp_image.show()

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
