from gi.repository import Gio
from PIL import Image
from PIL.ImageOps import fit
from os import environ as Env
from subprocess import run
import re

TMP_DIR = '/tmp/HydraPaper/'
SWAY_CONF_PATH = f'{Env.get("HOME")}/.config/sway/config'
SWAYLOCK_CONF_PATH = f'{Env.get("HOME")}/.swaylock/config'


def multi_setup_pillow(monitors, save_path, wp_setter_func=None):
    images = list(map(Image.open, [m.wallpaper for m in monitors]))
    resolutions = [
        (m.width * m.scaling, m.height * m.scaling) for m in monitors
    ]
    offsets = [(m.offset_x, m.offset_y) for m in monitors]

    final_image_width = max([
        m.offset_x + m.width * m.scaling for m in monitors
    ])
    final_image_height = max([
        m.offset_y + m.height * m.scaling for m in monitors
    ])

    n_images = [fit(i, r, method=Image.LANCZOS) for i, r in zip(images, resolutions)]
    final_image = Image.new('RGB', (final_image_width, final_image_height))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)


def set_wallpaper_gnome(path, wp_mode='spanned', lockscreen=False):
    gsettings_path = (
        'org.gnome.desktop.screensaver' if lockscreen
        else'org.gnome.desktop.background'
    )
    gsettings = Gio.Settings.new(gsettings_path)
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, wp_mode)


def set_wallpaper_mate(path, wp_mode='spanned', lockscreen=False):
    if lockscreen:
        print('Lock screen wallpaper on MATE unsupported')
        return
    gsettings = Gio.Settings.new('org.mate.background')
    wp_key = 'picture-filename'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, path)
    gsettings.set_string(mode_key, wp_mode)


def set_wallpaper_sway(monitors, lockscreen=False):
    conf_path = SWAYLOCK_CONF_PATH if lockscreen else SWAY_CONF_PATH
    with open(conf_path) as fd:
        conf = fd.read()
        fd.close()
    if lockscreen:
        n_conf = re.sub(r'image=.*', '', conf).strip()
        n_conf += '\n' + '\n'.join([
            f'image={m.name}:{m.wallpaper.replace(":", "::")}' for m in monitors
        ])
    else:
        n_conf = re.sub(r'output .* bg .*', '', conf).strip()
        n_conf += '\n' + '\n'.join([
            f'output {m.name} bg {m.wallpaper} fill' for m in monitors
        ])
    with open(conf_path, 'w') as fd:
        fd.write(n_conf)
        fd.close()
    run('sway reload'.split(' '))
