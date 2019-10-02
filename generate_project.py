import json
import sys
try:
    import yaml
except ImportError:
    print('Error: yaml not installed. Install with:\npip install pyyaml\nor\nconda install pyyaml')
    sys.exit()
import os
import shutil
from distutils.dir_util import copy_tree
from fileinput import FileInput
import textwrap


def load_settings(file):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def replace_in_file(file, find, replace_):
    for line in FileInput(file, inplace=True):
        print(line.replace(find, replace_), end='')


def remove_line(file, find):
    find_nl = f'{find}\n'
    for line in FileInput(file, inplace=True):
        if line != find_nl:
            print(line, end='')


def find_replace(directory, find, replace):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            filepath = os.path.join(path, filename)
            replace_in_file(filepath, find, replace)


here = os.path.dirname(os.path.abspath(__file__))
template_dir = f'{here}/template'
build_dir = f'{here}/build'
target_dir = f'{here}/..'

if not os.path.exists(f'{target_dir}/ipyvuelink.yaml'):
    print('Error: ipyvuelink.yaml is missing.')
    sys.exit(1)

settings = load_settings(f'{target_dir}/ipyvuelink.yaml')

placeholder = 'pL4C3h0ld3r'
ipy_placeholder = f'ipy{placeholder}'
jupyter_placeholder = f'jupyter-{placeholder}'

name = settings["extension_name"]
ipy_name = f'ipy{name}'
jupyter_name = f'jupyter-{name}'

single = settings['entry'].endswith('.vue')
view_type = settings['variant'].capitalize()

target_package_json = json.loads(open(f'{target_dir}/package.json').read())
version = target_package_json['version']

traitlet_mapping = {
    'String': 'Unicode',
    'Array': 'List',
    'Integer': 'Integer',
    'Float': 'Float',
    'Object': 'Dict',
    'Boolean': 'Boolean',
    'Any': 'Any'
}


def gen_py_component(component):
    name, props = component
    props = list(props['properties'].items())

    trait_list = set([traitlet_mapping[ptype] for pname, ptype in props] + ['Unicode'])
    traits = ', '.join(trait_list)

    prop_lines = [f"{pname} = {traitlet_mapping[ptype]}().tag(sync=True)" for pname, ptype in props]
    props_str = '\n            '.join(prop_lines)

    return textwrap.dedent(f"""
        from traitlets import ({traits})
        from ipyvue import VueWidget
        from ._version import semver


        class {name}(VueWidget):
            _model_name = Unicode('{name}Model').tag(sync=True)
            _view_name = Unicode('{view_type}View').tag(sync=True)
            _view_module = Unicode('{jupyter_name}').tag(sync=True)
            _model_module = Unicode('{jupyter_name}').tag(sync=True)
            _view_module_version = Unicode(semver).tag(sync=True)
            _model_module_version = Unicode(semver).tag(sync=True)
            {props_str}


        __all__ = ['{name}']
    """[1:-1])


def gen_js_component(component):
    name, props = component
    props = list(props['properties'].items())

    prop_lines = [f"{pname}: null," for pname, _ in props]
    props_str = '\n                        '.join(prop_lines)

    import_variant = 'LinkedComponent' if single else f"{{ {name} as LinkedComponent }}"

    return textwrap.dedent(f"""
        /* eslint camelcase: off */
        import {{ VueModel }} from 'jupyter-vue';
        import '../../vue_project_dist_mirror/component.css';
        import {import_variant} from '../../vue_project_dist_mirror/component.umd';

        export class {name}Model extends VueModel {{
            defaults() {{
                return {{
                    ...super.defaults(),
                    ...{{
                        _model_name: '{name}Model',
                        _view_name: '{view_type}View',
                        _view_module: '{jupyter_name}',
                        _model_module: '{jupyter_name}',
                        _view_module_version: '^{version}',
                        _model_module_version: '^{version}',
                        {props_str}
                    }},
                }};
            }}

            getVueTag() {{
                return LinkedComponent;
            }}
        }}

        {name}Model.serializers = {{
            ...VueModel.serializers,
        }};
    """[1:-1])


def gen_widget_files(component):
    name, _ = component
    with open(f'{build_dir}/{ipy_name}/{name}.py', 'w') as file:
        file.write(gen_py_component(component))

    with open(f'{build_dir}/js/src/models/{name}Model.js', 'w') as file:
        file.write(gen_js_component(component))


def gen_init_py(components):
    names = [f[0] for f in components]
    lines = "\n".join([f'from .{name} import *  # noqa: F401, F403' for name in names])
    replace_in_file(f'{build_dir}/{ipy_name}/__init__.py', '# imports placeholder', lines)


def gen_index_js(components):
    names = [f[0] for f in components]
    lines = "\n".join([f"export {{ {name}Model }} from './{name}Model';" for name in names])

    with open(f'{build_dir}/js/src/models/index.js', 'w') as file:
        file.write(lines + '\n')


def generate(force=False):
    if os.path.exists(f'{build_dir}/.ok') and not force:
        print('Project already generated')
        return

    if force:
        try:
            shutil.rmtree(build_dir)
        except OSError as e:
            print(e)

    print('Generating project')
    copy_tree(template_dir, build_dir)
    shutil.move(f'{build_dir}/{ipy_placeholder}/', f'{build_dir}/{ipy_name}')
    os.rename(f'{build_dir}/{jupyter_placeholder}.json', f'{build_dir}/{jupyter_name}.json')
    find_replace(build_dir, ipy_placeholder, ipy_name)
    find_replace(build_dir, jupyter_placeholder, jupyter_name)

    has_licence = os.path.isfile(f'{target_dir}/LICENSE')
    if has_licence:
        shutil.copyfile(f'{target_dir}/LICENSE', f'{build_dir}/LICENSE')
    else:
        remove_line(f'{build_dir}/MANIFEST.in', 'include LICENSE')

    replace_in_file(
        f'{build_dir}/js/package.json',
        '"version": "0.1.0",',
        f'"version": "{version}",')

    replace_in_file(
        f'{build_dir}/{ipy_name}/_version.py',
        '0, 0, 1',
        ', '.join(version.split('.')))

    if settings['variant'] == 'bootstrapvue':
        replace_in_file(f'{build_dir}/js/src/index.js',
                        "export { VuetifyView } from './vuetify/VuetifyView';",
                        "export { BootstrapvueView } from './bootstrapvue/BootstrapvueView';")

    components = list(settings['components'].items())
    for component in components:
        gen_widget_files(component)
    gen_index_js(components)
    gen_init_py(components)
    with open(f'{build_dir}/.ok', 'w') as file:
        file.write('ok\n')
