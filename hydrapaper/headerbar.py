from gi.repository import Gtk, Handy
from .wallpapers_folders_view import HydraPaperWallpapersFoldersView
from .confManager import ConfManager
from .slideshow_listbox_row import SlideshowListboxRow
import dbus


class HydraPaperHeaderbar(Handy.HeaderBar):
    def __init__(self, window, apply_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confman = ConfManager()
        self.apply_handler = apply_handler
        self.set_show_title_buttons(True)
        self.stack_switcher = Handy.ViewSwitcher()
        self.squeezer = Handy.Squeezer()
        self.nobox = Gtk.Label()
        self.bottom_bar = window.bottom_bar
        self.squeezer.add(self.stack_switcher)
        self.squeezer.add(self.nobox)
        self.squeezer.connect('notify::visible-child', self.on_squeeze)
        self.set_title_widget(self.squeezer)

        self.folders_view = HydraPaperWallpapersFoldersView(window)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/headerbar.ui'
        )
        self.wallpapers_folders_popover = self.builder.get_object(
            'wallpapersFoldersPopover'
        )
        self.wallpapers_folders_popover.set_child(self.folders_view)
        self.menu_popover = self.builder.get_object('menuPopover')
        self.apply_button = self.builder.get_object('applyButton')
        self.apply_button.connect('clicked', self.on_applyButton_clicked)
        self.menu_button = self.builder.get_object('menuBtn')
        self.wallpapers_folders_button = self.builder.get_object(
            'wallpapersFoldersBtn'
        )

        self.add_to_slideshow_btn = self.builder.get_object(
            'add_to_slideshow_btn'
        )
        self.add_to_slideshow_btn.connect('clicked', self.on_add_to_slideshow)
        self.slideshow_menu_btn = self.builder.get_object(
            'slideshow_menu_btn'
        )
        self.slideshow_switch = self.builder.get_object(
            'slideshow_switch'
        )
        self.slideshow_switch.set_state(
            self.confman.conf['Daemon']['wallpaper_rotation_enabled']
        )
        self.slideshow_switch.connect(
            'state-set', self.on_slideshow_mode_changed
        )
        self.slideshow_time_spinbutton = self.builder.get_object(
            'slideshow_time_spinbutton'
        )
        self.slideshow_time_spinbutton.set_increments(1, 10)
        self.slideshow_time_spinbutton.set_range(0, 300000)
        self.slideshow_time_spinbutton.set_value(
            self.confman.conf['Daemon']['wallpaper_rotation_sleep_time']
        )
        self.slideshow_time_spinbutton.connect(
            'value-changed', self.on_slideshow_time_spinbutton_changed
        )
        self.slideshow_listbox = self.builder.get_object('slideshow_listbox')
        self.slideshow_listbox.populate = self.populate_slideshow_listbox
        self.on_slideshow_mode_changed()
        self.populate_slideshow_listbox()

        left_widgets = [self.wallpapers_folders_button]
        right_widgets = [
            self.menu_button,
            self.apply_button,
            self.slideshow_menu_btn,
            self.add_to_slideshow_btn
        ]
        for w in left_widgets:
            self.pack_start(w)
        for w in right_widgets:
            self.pack_end(w)

        self.ww_popover = Gtk.Popover()
        self.ww_popover_content_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/which_wallpaper_box.ui'
        )
        self.ww_container = self.ww_popover_content_builder.get_object(
            'ww_container'
        )
        self.ww_popover_content_builder.get_object(
            'desktop_btn'
        ).connect('clicked', self.on_desktop_clicked)
        self.ww_popover_content_builder.get_object(
            'lockscreen_btn'
        ).connect('clicked', self.on_lockscreen_clicked)
        self.ww_popover_content_builder.get_object(
            'both_btn'
        ).connect('clicked', self.on_both_clicked)
        self.ww_popover.set_child(self.ww_container)
        self.ww_popover.set_autohide(True)
        self.ww_popover.set_parent(self.apply_button)

    def signal_daemon(self):
        bus = dbus.SessionBus()
        d = bus.get_object(
            'org.gabmus.hydrapaper.Daemon',
            '/org/gabmus/hydrapaper/Daemon'
        )
        iface = dbus.Interface(
            d, dbus_interface='org.gabmus.hydrapaper.Daemon.update_config'
        )
        iface.update_config()

    def on_slideshow_time_spinbutton_changed(self, *args):
        self.confman.conf['Daemon']['wallpaper_rotation_sleep_time'] = \
            self.slideshow_time_spinbutton.get_value()
        self.confman.save_conf()
        self.signal_daemon()

    def on_add_to_slideshow(self, *args):
        monitors = self.get_root().monitors_flowbox.get_monitors()
        pics = [m.wallpaper for m in monitors]
        if None in pics:
            return
        self.confman.conf['Daemon']['rotating_wallpapers'].append(pics)
        self.confman.save_conf()
        self.signal_daemon()
        self.populate_slideshow_listbox()

    def populate_slideshow_listbox(self, *args):
        child = self.slideshow_listbox.get_first_child()
        while child is not None:
            self.slideshow_listbox.remove(child)
            child = self.slideshow_listbox.get_first_child()
        for pics in self.confman.conf['Daemon']['rotating_wallpapers']:
            self.slideshow_listbox.append(
                SlideshowListboxRow(pics)
            )
        self.signal_daemon()

    def on_slideshow_mode_changed(self, *args):
        n_state = self.slideshow_switch.get_active()
        self.confman.conf['Daemon']['wallpaper_rotation_enabled'] = n_state
        self.confman.save_conf_async()
        sc = self.slideshow_menu_btn.get_style_context()
        for c in [f'slideshow-btn-{p}active' for p in ('', 'in')]:
            sc.remove_class(c)
        if n_state:
            sc.add_class('slideshow-btn-active')
            self.add_to_slideshow_btn.set_visible(True)
        else:
            sc.add_class('slideshow-btn-inactive')
            self.add_to_slideshow_btn.set_visible(False)
        self.signal_daemon()

    def on_squeeze(self, *args):
        self.bottom_bar.set_reveal(
            self.squeezer.get_visible_child() == self.nobox
        )

    def on_applyButton_clicked(self, btn):
        if self.confman.has_lockscreen_wallpaper:
            self.ww_popover.popup()
        else:
            self.apply_handler(self.apply_button, lockscreen=False)

    def on_desktop_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=False)

    def on_lockscreen_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=True)

    def on_both_clicked(self, btn):
        self.ww_popover.popdown()
        self.apply_handler(self.apply_button, lockscreen=False)
        self.apply_handler(self.apply_button, lockscreen=True)
