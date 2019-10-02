import os
import sys
import textwrap
from fileinput import FileInput
from distutils.dir_util import copy_tree
import shutil
from subprocess import check_call

try:
    import yaml
except ImportError:
    print('Error: yaml not installed. Install with:\npip install pyyaml\nor\nconda install pyyaml')
    sys.exit(1)


def load_settings(file):
    if not os.path.exists(file):
        print(f'Error: {file} is missing.')
        sys.exit(1)

    with open(file, 'r') as stream:
        return yaml.safe_load(stream)


def replace_in_file(file, find, replace):
    for line in FileInput(file, inplace=True):
        print(line.replace(find, replace), end='')


def remove_line(file, find):
    find_nl = f'{find}\n'
    for line in FileInput(file, inplace=True):
        if line != find_nl:
            print(line, end='')


def replace_in_directory(directory, find, replace):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            filepath = os.path.join(path, filename)
            replace_in_file(filepath, find, replace)


def write_file(path, content):
    with open(path, 'w') as file:
        file.write(content)


def copy_directory_recursive(src, dest):
    copy_tree(src, dest)


def directory_exists(path):
    return os.path.exists(path)


def delete_directory(path):
    try:
        shutil.rmtree(path)
    except OSError:
        pass


def rename_directory(old, new):
    shutil.move(old, new)


def rename_file(old, new):
    os.rename(old, new)


def file_exists(path):
    return os.path.isfile(path)


def copy_file(src, dest):
    shutil.copyfile(src, dest)


def fix_indentation(template):
    return textwrap.dedent(template[1:-1])


def execute(path, command):
    check_call(command, cwd=path, shell=True)
