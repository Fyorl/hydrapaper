from gi.repository import Gio
from PIL import Image
from PIL.ImageOps import fit
from os import environ as Env
from subprocess import run
import re

TMP_DIR = '/tmp/HydraPaper/'
SWAY_CONF_PATH = f'{Env.get("HOME")}/.config/sway/config'
SWAYLOCK_CONF_PATH = f'{Env.get("HOME")}/.swaylock/config'


def cut_image(image_path, resolution, save_path):
    with Image.open(image_path) as image:
        n_image = fit(
            image,
            resolution,
            method=Image.LANCZOS, centering=(0.5, 0.5)
        )
        n_image.save(save_path)


def get_combined_resolution(monitors):
    return (
        max([
            m.offset_x + m.width * m.scaling for m in monitors
        ]),
        max([
            m.offset_y + m.height * m.scaling for m in monitors
        ])
    )


def multi_setup_pillow(monitors, save_path, wp_setter_func=None):
    images = list(map(Image.open, [m.wallpaper for m in monitors]))
    resolutions = [
        (m.width * m.scaling, m.height * m.scaling) for m in monitors
    ]
    offsets = [(m.offset_x, m.offset_y) for m in monitors]

    final_image_width, final_image_height = get_combined_resolution(monitors)

    n_images = [fit(i, r, method=Image.LANCZOS) for i, r in zip(images, resolutions)]
    final_image = Image.new('RGB', (final_image_width, final_image_height))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)
    for i in images:
        i.close()


def __set_wallpaper_gsettings(gsettings_path, wp_key, mode_key, path, wp_mode):
    gsettings = Gio.Settings.new(gsettings_path)
    gsettings.set_string(wp_key, path)
    gsettings.set_string(mode_key, wp_mode)

def set_wallpaper_gnome(path, wp_mode='spanned', lockscreen=False):
    __set_wallpaper_gsettings(
        gsettings_path=(
            'org.gnome.desktop.screensaver' if lockscreen
            else'org.gnome.desktop.background'
        ),
        wp_key='picture-uri',
        mode_key='picture-options',
        path='file://{}'.format(path),
        wp_mode=wp_mode
    )


def set_wallpaper_cinnamon(path, wp_mode='spanned', lockscreen=False):
    if lockscreen:
        print('Lock screen wallpaper on Cinnamon unsupported')
        return
    __set_wallpaper_gsettings(
        gsettings_path=(
            'org.cinnamon.desktop.screensaver' if lockscreen
            else'org.cinnamon.desktop.background'
        ),
        wp_key='picture-uri',
        mode_key='picture-options',
        path='file://{}'.format(path),
        wp_mode=wp_mode
    )


def set_wallpaper_mate(path, wp_mode='spanned', lockscreen=False):
    if lockscreen:
        print('Lock screen wallpaper on MATE unsupported')
        return
    __set_wallpaper_gsettings(
        gsettings_path='org.mate.background',
        wp_key='picture-filename',
        mode_key='picture-options',
        path=path,
        wp_mode=wp_mode
    )


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
