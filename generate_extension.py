from config import (
    template_extension_dir, extension_dir, vue_project_dir, settings, ipy_placeholder,
    jupyter_placeholder, ipy_extension_name, jupyter_extension_name, single_component_mode,
    component_library_used, jupyter_extension_version)
from helpers import (
    replace_in_file, remove_line, replace_in_directory, write_file, copy_directory_recursive,
    rename_directory, rename_file, file_exists, copy_file, fix_indentation)


def generate_extension():
    copy_directory_recursive(
        src=template_extension_dir,
        dest=extension_dir)

    rename_directory(
        old=f'{extension_dir}/{ipy_placeholder}/',
        new=f'{extension_dir}/{ipy_extension_name}')

    rename_file(
        old=f'{extension_dir}/{jupyter_placeholder}.json',
        new=f'{extension_dir}/{jupyter_extension_name}.json')

    replace_in_directory(
        directory=extension_dir,
        find=ipy_placeholder,
        replace=ipy_extension_name)

    replace_in_directory(
        directory=extension_dir,
        find=jupyter_placeholder,
        replace=jupyter_extension_name)

    replace_in_file(
        file=f'{extension_dir}/js/package.json',
        find='"version": "0.1.0",',
        replace=f'"version": "{jupyter_extension_version}",')

    replace_in_file(
        file=f'{extension_dir}/{ipy_extension_name}/_version.py',
        find='0, 0, 1',
        replace=', '.join(jupyter_extension_version.split('.')))

    if component_library_used == 'bootstrapvue':
        replace_in_file(
            file=f'{extension_dir}/js/src/index.js',
            find="export { VuetifyView } from './vuetify/VuetifyView';",
            replace="export { BootstrapvueView } from './bootstrapvue/BootstrapvueView';")

    vue_components = list(settings['components'].items())

    for vue_component in vue_components:
        name, props = vue_component
        generate_py_component(f'{extension_dir}/{ipy_extension_name}/{name}.py', name, props)
        generate_js_component(f'{extension_dir}/js/src/models/{name}Model.js', name, props)

    generate_init_py(f'{extension_dir}/{ipy_extension_name}/__init__.py', vue_components)
    generate_index_js(f'{extension_dir}/js/src/models/index.js', vue_components)

    copy_license()


def generate_py_component(path, name, props):
    props = list(props['properties'].items())

    trait_list = set([traitlet_mapping[ptype] for pname, ptype in props] + ['Unicode'])
    traits = ', '.join(trait_list)

    prop_lines = [f"{pname} = {traitlet_mapping[ptype]}().tag(sync=True)" for pname, ptype in props]
    props_str = '\n            '.join(prop_lines)

    content = fix_indentation(f"""
        from traitlets import ({traits})
        from ipyvue import VueWidget
        from ._version import semver


        class {name}(VueWidget):
            _model_name = Unicode('{name}Model').tag(sync=True)
            _view_name = Unicode('{view_name}').tag(sync=True)
            _view_module = Unicode('{jupyter_extension_name}').tag(sync=True)
            _model_module = Unicode('{jupyter_extension_name}').tag(sync=True)
            _view_module_version = Unicode(semver).tag(sync=True)
            _model_module_version = Unicode(semver).tag(sync=True)
            {props_str}


        __all__ = ['{name}']
    """)

    write_file(path, content)


traitlet_mapping = {
    'String': 'Unicode',
    'Array': 'List',
    'Integer': 'Integer',
    'Float': 'Float',
    'Object': 'Dict',
    'Boolean': 'Bool',
    'Any': 'Any'
}


def generate_js_component(path, name, props):
    props = list(props['properties'].items())

    prop_lines = [f"{pname}: null," for pname, _ in props]
    props_str = '\n                        '.join(prop_lines)

    import_variant = \
        'LinkedComponent' if single_component_mode else f"{{ {name} as LinkedComponent }}"

    content = fix_indentation(f"""
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
                        _view_name: '{view_name}',
                        _view_module: '{jupyter_extension_name}',
                        _model_module: '{jupyter_extension_name}',
                        _view_module_version: '^{jupyter_extension_version}',
                        _model_module_version: '^{jupyter_extension_version}',
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
    """)

    write_file(path, content)


view_name = f'{component_library_used.capitalize()}View'


def generate_init_py(path, components):
    names = [f[0] for f in components]
    lines = "\n".join([f'from .{name} import *  # noqa: F401, F403' for name in names])
    replace_in_file(path, '# imports placeholder', lines)


def generate_index_js(path, components):
    names = [f[0] for f in components]
    lines = "\n".join([f"export {{ {name}Model }} from './{name}Model';" for name in names])

    write_file(path, lines)


def copy_license():
    if file_exists(f'{vue_project_dir}/LICENSE'):
        copy_file(f'{vue_project_dir}/LICENSE', f'{extension_dir}/LICENSE')
    else:
        remove_line(f'{extension_dir}/MANIFEST.in', 'include LICENSE')
