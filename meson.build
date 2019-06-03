project('hydrapaper',
    version: '1.6',
    meson_version: '>= 0.40.0',
    license: 'GPL3'
)

description = 'Wallpaper manager with multimonitor support for GNOME'
prettyname = 'HydraPaper'
prettylicense = 'GPL-3.0+'

author = 'gabmus'
authorfullname = 'Gabriele Musco'
authoremail = 'emaildigabry@gmail'
domain = 'org'
# app_id built as: domain.author.project_name
gitrepo = 'https://gitlab.com/'+author+'/'+meson.project_name()

# NOTE: if you contributed, feel free to add your name and email address here
contributors = '\n'.join([
    'Gabriele Musco (GabMus) &lt;emaildigabry@gmail.com&gt;',
    'Alex Hunt (huntie) &lt;hello@alexhunt.io&gt;'
])

# i18n = import('i18n')
python = import('python3')
gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = join_paths(prefix, python.sysconfig_path('purelib'))

install_subdir(meson.project_name(), install_dir: pythondir)
subdir('data')
subdir('bin')
