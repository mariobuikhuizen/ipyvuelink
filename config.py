import json
import os
from helpers import load_settings

here = os.path.dirname(os.path.abspath(__file__))
template_extension_dir = f'{here}/extension_template'
extension_dir = f'{here}/extension'
vue_project_dir = f'{here}/..'

settings = load_settings(f'{vue_project_dir}/ipyvuelink.yaml')

placeholder = 'pL4C3h0ld3r'
ipy_placeholder = f'ipy{placeholder}'
jupyter_placeholder = f'jupyter-{placeholder}'

extension_name = settings["extension_name"]
ipy_extension_name = f'ipy{extension_name}'
jupyter_extension_name = f'jupyter-{extension_name}'

single_component_mode = settings['entry'].endswith('.vue')
component_library_used = settings['component_library_used']

vue_package_json = json.loads(open(f'{vue_project_dir}/package.json').read())
jupyter_extension_version = vue_package_json['version']
