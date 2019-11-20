import argparse

from config import (extension_dir, vue_project_dir, settings, ipy_extension_name,
                    jupyter_extension_name)
from helpers import delete_directory, directory_exists, execute
from generate_extension import generate_extension


def handle_command_line():
    parser = argparse.ArgumentParser(usage='''cli command

    commands:
        dev-install-extension   Generate the jupyter-extension, build it and install in development
                                mode (notebook and lab). Run this once when:
                                  - starting or git cloning a project 
                                  - using a new environment
                                  - ipyvuelink.yaml has changed
                                  - the submodule ipyvuelink has changed
                                The 'watch-extension' has to be stopped before running.
        watch-vue-project       Build and watch vue-cli project.
        watch-extension         Build and watch extension.

        publish-local           Publish extension locally as a pip package (javascript included),
                                installable by running:
                                    pip install [extension_name]-[version].tar.gz  
        publish-pypi            Publish extension on PyPi.
        publish-npm             Publish extension on NPM.
    ''')

    parser.add_argument('command', type=str, help='The command')

    args = parser.parse_args()

    if args.command == 'dev-install-extension':
        dev_install_extension()
    elif args.command == 'watch-vue-project':
        build_vue_project(watch=True)
    elif args.command == 'watch-extension':
        watch_extension()
    elif args.command == 'regenerate-extension':
        regenerate_extension()
    elif args.command == 'publish-local':
        publish_local()
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


def build_vue_project(watch=False):
    if not directory_exists(f'{vue_project_dir}/node_modules'):
        execute(vue_project_dir, 'yarn install')

    try:
        # keep using --mode production with --watch, else css is not included
        execute(
            vue_project_dir,
            f'npx vue-cli-service build --target lib \
            --formats {"umd"} \
            --dest {extension_dir}/js/vue_project_dist_mirror \
            --name component src/{settings["entry"]} \
            --mode production \
            {"--watch" if watch else ""}')
    except KeyboardInterrupt:
        pass


def watch_extension():
    try:
        install_extension_dependencies()
        execute(f'{extension_dir}/js', 'npm run watch')
    except KeyboardInterrupt:
        pass


def publish_local():
    regenerate_extension()
    execute(extension_dir, f'python setup.py sdist --dist-dir={vue_project_dir}')

def publish_pypi():
    print('Not yet implemented')


def publish_npm():
    regenerate_extension()
    execute(f'{extension_dir}/js', 'npm publish --public')


# helpers #


def install_extension_dependencies():
    if not directory_exists(f'{extension_dir}/js/node_modules'):
        execute(f'{extension_dir}/js', f'npm install')


def build_extension():
    install_extension_dependencies()
    execute(f'{extension_dir}/js', f'npm run prepare')


def regenerate_extension():
    delete_directory(extension_dir)
    generate_extension()
    build_vue_project()
    build_extension()
