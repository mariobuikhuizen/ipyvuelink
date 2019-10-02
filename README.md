# ipyvuelink

Create Jupyter widgets from a Vue CLI project.

Examples: [ipyvuelink-example-1](https://github.com/mariobuikhuizen/ipyvuelink-example-1/tree/ipyvuelink),
[2](https://github.com/mariobuikhuizen/ipyvuelink-example-2/tree/ipyvuelink) and
[3](https://github.com/mariobuikhuizen/ipyvuelink-example-3/tree/ipyvuelink). See example
[4](https://github.com/mariobuikhuizen/ipyvuelink-example-4) for a project with multiple widgets.

## Usage

### Setup
* Create file ipyvuelink.yaml with extension name, widgets and properties (see examples)
* Add ipyvuelink as git submodule in your project:
`$ git submodule add https://github.com/mariobuikhuizen/ipyvuelink.git`

### Development

#### Once:
```
$ ipyvuelink/cli install-dev
```

#### Each session:

1. In terminal 1: `$ yarn serve`
2. In terminal 2: `$ ipyvuelink/cli watch`
3. In terminal 3: `$ jupyter notebook yourNotebook.ipynb` (or `$ jupyter lab yourNotebook.ipynb --watch` for Lab)
4. Change code
5. See changes in hot reloaded app on `http://localhost:8080`
6. Goto 4 until ready to test in notebook
7. In terminal 4: `$ ipyvuelink/cli build-lib`
8. See changes in notebook on `http://localhost:8888/notebooks/yourNotebook.ipynb`
   (after a page refresh) (or `http://localhost:8888/lab` for Lab)
9. Goto 4

#### When ipyvuelink.yaml changes:
```
$ ipyvuelink/cli regenerate-project
```

### Release

* Bump version in package.json
* Run `$ ipyvuelink/cli release-pypi` to release on PyPI
* Run `$ ipyvuelink/cli release-npm` to release on NPM
