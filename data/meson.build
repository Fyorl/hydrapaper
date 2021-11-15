conf = configuration_data()
conf.set('bindir', join_paths(prefix, bindir))
conf.set('prettyname', prettyname)
conf.set('appid', app_id)
conf.set('projectname', meson.project_name())
conf.set('libexecdir', libexecdir)
conf.set('apppath', app_id_aspath)

desktop_file = configure_file(
    input: app_id + '.desktop.in',
    output: app_id + '.desktop.i18n.in',
    configuration: conf
)

i18n.merge_file(
    input: desktop_file,
    output: app_id + '.desktop',
    po_dir: '../po',
    type: 'desktop',
    install: true,
    install_dir: join_paths(datadir, 'applications')
)

configure_file(
    input: app_id + '.service.in',
    output: app_id + '.service',
    configuration: conf,
    install_dir: dbus_service_dir
)

if enable_daemon
    configure_file(
        input: app_id + '.Daemon.service.in',
        output: app_id + '.Daemon.service',
        configuration: conf,
        install: true,
        install_dir: dbus_service_dir
    )

    configure_file(
        input: app_id + '.Daemon.service.systemd.in',
        output: app_id + 'd.service',
        configuration: conf,
        install: true,
        install_dir: systemd_user_unit_dir
    )

    daemon_desktop_file = configure_file(
        input: app_id + '.Daemon.desktop.in',
        output: app_id + '.Daemon.desktop.i18n.in',
        configuration: conf
    )

    i18n.merge_file(
        input: daemon_desktop_file,
        output: app_id + '.Daemon.desktop',
        po_dir: '../po',
        type: 'desktop',
        install: true,
        # install_dir: join_paths(etcdir, 'xdg', 'autostart')
        install_dir: join_paths(datadir, 'applications')
    )
endif

configure_file(
    input: app_id + '.gschema.xml.in',
    output: app_id + '.gschema.xml',
    configuration: conf,
    install_dir: join_paths(datadir, 'glib-2.0/schemas')
)

icondir = join_paths(datadir, 'icons/hicolor')
install_data(
    'icons/'+app_id+'.svg',
    install_dir: join_paths(icondir, 'scalable/apps')
)
install_data(
    'icons/'+app_id+'-symbolic.svg',
    install_dir: join_paths(icondir, 'symbolic/apps')
)

subdir('ui')

app_resources = gnome.compile_resources(app_id,
    app_id + '.gresource.xml',
    gresource_bundle: true,
    dependencies: configure_file(
        input: 'ui/aboutdialog.ui.in',
        output: 'aboutdialog.ui',
        configuration: ui_conf
    ),
    install: true,
    install_dir: pkgdatadir
)

app_settings = gnome.compile_schemas()

#appdata_conf = configuration_data()
#appdata_conf.set('authorfullname', authorfullname)
#appdata_conf.set('gitrepo', gitrepo)
#appdata_conf.set('website', website)
#appdata_conf.set('authoremail', authoremail)
#appdata_conf.set('prettyname', prettyname)
#appdata_conf.set('appid', app_id)
#appdata_conf.set('prettylicense', prettylicense)
#
#configure_file(
#    input: appdata_file,
#    output: app_id + '.appdata.xml.',
#    configuration: appdata_conf,
#    install: true,
#    install_dir: join_paths(datadir, 'metainfo')
#)

ascli_exe = find_program('appstreamcli', required: false)
if ascli_exe.found()
    test(
        'validate metainfo file',
        ascli_exe,
        args: [
            'validate',
            #'--no-net',
            #'--pedantic',
            'data/' + app_id + '.appdata.xml'
        ]
    )
endif

i18n.merge_file(
    input: app_id + '.appdata.xml.in',
    output: app_id + '.appdata.xml',
    po_dir: '../po',
    install: true,
    install_dir: join_paths(datadir, 'metainfo')
)
