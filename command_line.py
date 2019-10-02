import argparse
from subprocess import CalledProcessError

from config import (extension_dir, vue_project_dir, settings, ipy_extension_name,
                    jupyter_extension_name, component_library_used)
from helpers import copy_directory_recursive, delete_directory, directory_exists, execute
from generate_extension import generate_extension


def handle_command_line():
    parser = argparse.ArgumentParser(usage='''cli command

    commands:
        install-dev             Generates jupyter-extension project, builds it and installs in
                                developement mode (notebook and lab). This has to be done only once.
        build-lib               Builds vue-cli project with target lib. Use this when code has
                                changed.
        watch                   Runs JavaScript build in watch mode.
        regenerate-project      Regenerated project. Use this when ipyvuelink.yaml has changed
        publish-pypi            Publish extension on PyPi.
        publish-npm             Publish extension on NPM.
    ''')

    parser.add_argument('command', type=str, help='The command')

    args = parser.parse_args()

    if args.command == 'install-dev':
        dev_install_extension()
    elif args.command == 'build-lib':
        build_vue_project()
    elif args.command == 'watch':
        watch_extension()
    elif args.command == 'regenerate-project':
        regenerate_extension()
    elif args.command == 'publish-pypi':
        publish_pypi()
    elif args.command == 'publish-npm':
        publish_npm()
    else:
        print(f'Unknown command: {args.command}')


# Commands #


def dev_install_extension():
    delete_directory(extension_dir)
    generate_extension()
    build_vue_project()
    execute(None, f'jupyter nbextension uninstall {jupyter_extension_name}')
    execute(None, f'pip install -e {extension_dir}')
    execute(None, f'jupyter nbextension install --py --symlink --sys-prefix {ipy_extension_name}')
    execute(None, f'jupyter nbextension enable --py --sys-prefix {ipy_extension_name}')
    execute(None, f'jupyter labextension install {extension_dir}/js --no-build')


def build_vue_project():
    temporary_remove_vuetify_loader_and_execute(
        _build_vue_project)

    copy_directory_recursive(
        f'{vue_project_dir}/dist',
        f'{extension_dir}/js/vue_project_dist_mirror')


def watch_extension():
    try:
        install_extension_dependencies()
        execute(f'{extension_dir}/js', 'npm run watch')
    except KeyboardInterrupt:
        pass


def regenerate_extension():
    delete_directory(extension_dir)
    generate_extension()
    build_vue_project()
    build_extension()


def publish_pypi():
    print('Not yet implemented')


def publish_npm():
    regenerate_extension()
    execute(f'{extension_dir}/js', 'npm publish --public')


# helpers #


def temporary_remove_vuetify_loader_and_execute(callable):
    vuetify_loader_removed = False
    if component_library_used == 'vuetify':
        # Remove vuetify-loader, so we can load a Jupyter compatible version of Vuetify. Ideally
        # this should be configured with vue-cli, but I've not yet figured out how to do that.
        try:
            execute(vue_project_dir, 'yarn remove vuetify-loader')
            vuetify_loader_removed = True
        except CalledProcessError:
            pass
    try:
        callable()
    finally:
        # Undo the removal of vuetify-loader, so yarn serve works again.
        if vuetify_loader_removed:
            execute(vue_project_dir, 'yarn add vuetify-loader@^1.2.2 --dev')


def _build_vue_project():
    if not directory_exists(f'{vue_project_dir}/node_modules'):
        execute(vue_project_dir, 'yarn install')

    execute(
        vue_project_dir,
        f'npx vue-cli-service build --target lib --name component src/{settings["entry"]}')


def install_extension_dependencies():
    if not directory_exists(f'{extension_dir}/js/node_modules'):
        execute(f'{extension_dir}/js', f'npm install')


def build_extension():
    install_extension_dependencies()
    execute(f'{extension_dir}/js', f'npm run prepare')
