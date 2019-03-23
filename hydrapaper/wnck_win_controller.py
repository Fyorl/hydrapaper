from gi.repository import Gtk, Wnck
from time import time as timestamp

windows_to_restore = []

def change_minimize_state(toggle=None, state=None):
    if toggle and state == None:
        state = toggle.get_active()
    if state:
        if toggle:
            toggle.get_child().set_from_icon_name(
                'go-top-symbolic',
                Gtk.IconSize.BUTTON
            )
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation
        windows_to_restore = []
        for window in screen.get_windows():
            if not window.is_minimized() and
            not 'desktop' in window.get_application().get_name().lower() and
            window.get_application().get_name().lower() != 'hydrapaper':
                windows_to_restore.append(window)
                window.minimize()
    else:
        screen = Wnck.Screen.get_default()
        if screen:
            screen.force_update()  # recommended per Wnck documentation
        for window in windows_to_restore:
            if window.is_minimized():
                window.activate(timestamp())
        if screen:
            for window in screen.get_windows():
                if window.get_application().get_name().lower() == 'hydrapaper':
                    window.activate(timestamp())
                    break
