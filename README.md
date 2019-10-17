# ipyvuelink

Create Jupyter widgets from a Vue CLI project.

Examples: [ipyvuelink-example-1](https://github.com/mariobuikhuizen/ipyvuelink-example-1/tree/test-1b)
<!--- ,[2](https://github.com/mariobuikhuizen/ipyvuelink-example-2/tree/ipyvuelink) and
[3](https://github.com/mariobuikhuizen/ipyvuelink-example-3/tree/ipyvuelink). See example
[4](https://github.com/mariobuikhuizen/ipyvuelink-example-4) for a project with multiple widgets. --->


## Usage

### Minimal environment
```
$ conda create --name my-env -c conda-forge python pip jupyterlab ipywidgets pyyaml nodejs yarn
$ conda activate my-env
(my-env)$

# For Jupyter Lab:
(my-env)$ jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

### Setup
* Add `ipyvuelink.yaml` to the root of your Vue CLI project:
```yaml
# Name of the extension. This will turn into ipymyextension for the python part and jupyter-myextension for the 
# javascript part.
extension_name: myextension

# Entry point for ipyvuelink. This also supports multiple components when using an .js file with exports for
# these components, e.g: "export { default as Component2 } from './components/component2'" for component2.vue etc.
entry: components/mycomponent.vue

# Different workarounds are necessary to make Vuetify or BootstrapVue work inside a notebook. 
# vuetify | bootstrapvue
component_library_used: vuetify

# Components which are exposed.
components:
  Mycomponent:  # name(s) of the components(s) configured in the entry property above.  
    properties:
      # name: type.
      # - name in snake_case
      # - type: String | Integer | Float | Boolean | Object | Array | Any
      myprop: Object  # name(s) of the props(s) to be exposed.
      anotherprop: ...
  Conmponent2:
    ...
```
* Add ipyvuelink as git submodule to the root of your Vue CLI project:
`$ git submodule add https://github.com/mariobuikhuizen/ipyvuelink.git`
  * Note: when cloning or pulling from github, run `$ git submodule update --init`.
* Modify your vue components
  * Accept the properties configured in `ipyvuelink.yaml` as `props`, e.g.: `props: { myprop: Object }`.
  * Communicate changes by emitting an event with the name of the prop, e.g.: `$emit('myprop', ...)`.

### Development

#### Once:
```
(my-env)$ ipyvuelink/cli dev-install-extension
```
Also run this command when ipyvuelink.yaml or the submodule ipyvuelink has changed.

#### Each session:

1. In terminal 1: `(my-env)$ yarn serve`
2. In terminal 2: `(my-env)$ ipyvuelink/cli watch-vue-project`
3. In terminal 4: `(my-env)$ ipyvuelink/cli watch-extension`
4. In terminal 3: `(my-env)$ jupyter notebook yourNotebook.ipynb` (or `(ipyvuelink-env)$ jupyter lab yourNotebook.ipynb --watch` for Lab)
5. Change code
6. See changes in the hot reloaded app on `http://localhost:8080`
7. Goto 5 until ready to test in notebook
8. Refresh the page and see changes in the notebook on `http://localhost:8888/notebooks/yourNotebook.ipynb` (or `http://localhost:8888/lab` for Lab)
9. Goto 4

### Release

* Bump version in package.json
* Run `(my-env)$ ipyvuelink/cli release-pypi` to release on PyPI
* Run `(my-env)$ ipyvuelink/cli release-npm` to release on NPM
