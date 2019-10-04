import argparse

from config import (extension_dir, vue_project_dir, settings, ipy_extension_name,
                    jupyter_extension_name)
from helpers import delete_directory, directory_exists, execute
from generate_extension import generate_extension


def handle_command_line():
    parser = argparse.ArgumentParser(usage='''cli command

    commands:
        install-dev             Generates jupyter-extension project, builds it and installs in
                                developement mode (notebook and lab). This has to be done only once.
        watch-vue-project       Build and watch vue-cli project.
        watch-extension         Build and watch extension.
        regenerate-project      Regenerated project. Use this when ipyvuelink.yaml has changed
        publish-pypi            Publish extension on PyPi.
        publish-npm             Publish extension on NPM.
    ''')

    parser.add_argument('command', type=str, help='The command')

    args = parser.parse_args()

    if args.command == 'install-dev':
        dev_install_extension()
    elif args.command == 'watch-vue-project':
        build_vue_project(watch=True)
    elif args.command == 'watch-extension':
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


def install_extension_dependencies():
    if not directory_exists(f'{extension_dir}/js/node_modules'):
        execute(f'{extension_dir}/js', f'npm install')


def build_extension():
    install_extension_dependencies()
    execute(f'{extension_dir}/js', f'npm run prepare')
