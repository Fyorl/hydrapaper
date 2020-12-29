daemon_conf = configuration_data()
daemon_conf.set('PYTHON', python.find_python().path())

configure_file(
    input: meson.project_name() + 'd.in.py',
    output: meson.project_name() + 'd',
    install: true,
    install_dir: libexecdir,
    configuration: daemon_conf
)
