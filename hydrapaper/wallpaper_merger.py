from gi.repository import Gio
from PIL import Image
from PIL.ImageOps import fit
from os import Popen
from .confManager import ConfManager

TMP_DIR='/tmp/HydraPaper/'

def multi_setup_pillow(monitors, save_path, wp_setter_func=None):
    images = list(map(Image.open, [m.wallpaper for m in monitors]))
    resolutions = [(m.width * m.scaling, m.height * m.scaling) for m in monitors]
    offsets = [(m.offset_x, m.offset_y) for m in monitors]

    # DEBUG
    # for m in monitors:
    #     print(m)

    final_image_width = max([m.offset_x + m.width * m.scaling for m in monitors])
    final_image_height = max([m.offset_y + m.height * m.scaling for m in monitors])

    # DEBUG
    # print('Final Size: {} x {}'.format(final_image_width, final_image_height))

    n_images = []
    for i, r in zip(images, resolutions):
        n_images.append(fit(i, r, method=Image.LANCZOS))
    final_image = Image.new('RGB', (final_image_width, final_image_height))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)

def set_wallpaper_gnome(path, wp_mode='spanned'):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, wp_mode)

def set_wallpaper_mate(path, wp_mode='spanned'):
    # TODO make this work with plain Gio.Settings
    # As of now I can't seem to be able to set mate gsettings
    # If running under flatpak, for now getting out of the sandbox with
    # flatpak-spawn --host is the only way to properly support MATE
    confman = ConfManager()
    if confman.is_flatpak:
        cmds = [
            f'gsettings set org.mate.background picture-filename {path}',
            f'gsettings set org.mate.background picture-options {wp_mode}'
        ]
        for cmd in cmds:
            Popen(
                f'flatpak-spawn --host {cmd}',
                shell=True
            )
    else:
        gsettings = Gio.Settings.new('org.mate.background')
        wp_key = 'picture-filename'
        mode_key = 'picture-options'
        gsettings.set_string(wp_key, path)
        gsettings.set_string(mode_key, wp_mode)
