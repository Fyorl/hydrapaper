daemon_conf = configuration_data()
daemon_conf.set('PYTHON', python.find_python().path())

configure_file(
    input: app_id + '.Daemon.in.py',
    output: app_id + '.Daemon',
    install: true,
    install_dir: libexecdir,
    configuration: daemon_conf
)
