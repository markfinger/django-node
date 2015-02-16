Django Node
===========

Bindings and utils for integrating Node.js and NPM into a Django application.

```python
from django_node import node, npm
from django_node.server import server

# Run a particular file with Node.js
stderr, stdout = node.run('/path/to/some/file.js', '--some-argument')

# Call `npm install` within a particular directory
stderr, stdout = npm.install('/path/to/some/directory')

# Add a persistent service to a Node server controlled by your python process
service = server.add_service('/some-endpoint', '/path/to/some/file.js')

# Pass data to your service and output the result
print(service(some_param=10, another_param='foo').text)
```

Documentation
-------------

- [Installation](#installation)
- [Node.js](#nodejs)
  - [run()](#django_nodenoderun)
  - [ensure_installed()](#django_nodenodeensure_installed)
  - [ensure_version_gte()](#django_nodenodeensure_version_gte)
  - [is_installed](#django_nodenodeis_installed)
  - [version](#django_nodenodeversion)
  - [version_raw](#django_nodenodeversion_raw)
- [NPM](#npm)
  - [install()](#django_nodenpminstall)
  - [run()](#django_nodenpmrun)
  - [ensure_installed()](#django_nodenpmensure_installed)
  - [ensure_version_gte()](#django_nodenpmensure_version_gte)
  - [is_installed](#django_nodenpmis_installed)
  - [version](#django_nodenpmversion)
  - [version_raw](#django_nodenpmversion_raw)
- [Settings](#settings)
  - [PATH_TO_NODE](#django_nodepath_to_node)
  - [NODE_VERSION_COMMAND](#django_nodenode_version_command)
  - [NODE_VERSION_FILTER](#django_nodenode_version_filter)
  - [PATH_TO_NPM](#django_nodepath_to_npm)
  - [NPM_VERSION_COMMAND](#django_nodenpm_version_command)
  - [NPM_VERSION_FILTER](#django_nodenpm_version_filter)
  - [NPM_INSTALL_COMMAND](#django_nodenpm_install_command)
  - [NPM_INSTALL_PATH_TO_PYTHON](#django_nodenpm_install_path_to_python)
- [Running the tests](#running-the-tests)


Installation
------------

```bash
pip install django-node
```

Add `'django_node'` to your `INSTALLED_APPS`

```python
INSTALLED_APPS = (
    # ...
    'django_node',
)
```


Node.js
-------

The `django_node.node` module provides utils for introspecting and calling Node.js.

### django_node.node.run()

A method which will invoke Node.js with the arguments provided and return the resulting stderr and stdout.

Accepts an optional keyword argument, `production`, which will ensure that the command is run
with the `NODE_ENV` environment variable set to 'production'.

```
from django_node import node

stderr, stdout = node.run('/path/to/some/file.js', '--some-argument')

# With NODE_ENV set to production
stderr, stdout = node.run('/path/to/some/file.js', '--some-argument', production=True)
```

### django_node.node.ensure_installed()

A method which will raise an exception if Node.js is not installed.

### django_node.node.ensure_version_gte()

A method which will raise an exception if the installed version of Node.js is
less than the version required.

Arguments:

`version_required`: a tuple containing the minimum version required.

```python
from django_node import node

node_version_required = (0, 10, 0)

node.ensure_version_gte(node_version_required)
```

### django_node.node.is_installed

A boolean indicating if Node.js is installed.

### django_node.node.version

A tuple containing the version of Node.js installed. For example, `(0, 10, 33)`

### django_node.node.version_raw

A string containing the raw version returned from Node.js. For example, `'v0.10.33'`


NPM
---

The `django_node.npm` module provides utils for introspecting and calling NPM.

### django_node.npm.install()

A method that will invoke `npm install` in a specified directory. Optional arguments will be
appended to the invoked command.

Arguments:

- `target_dir`: a string pointing to the directory which the command will be invoked in.
- `*args`: optional strings to append to the invoked command.
- `silent`: an optional boolean indicating that NPM's output should not be printed to the terminal.

```python
from django_node import npm

# Install the dependencies in a particular directory
stderr, stdout = npm.install('/path/to/some/directory/')

# Install a dependency into a particular directory and persist it to the package.json file
stderr, stdout = npm.install('/path/to/some/directory/', '--save', 'some-package')

# Install dependencies but prevent NPM's output from being logged to the terminal
stderr, stdout = npm.install('/path/to/some/directory/', silent=True)
```

### django_node.npm.run()

A method which will invoke NPM with the arguments provided and return the resulting stderr and stdout.

```python
from django_node import npm

stderr, stdout = npm.run('install', '--save', 'some-package')
```

### django_node.npm.ensure_installed()

A method which will raise an exception if NPM is not installed.

### django_node.npm.ensure_version_gte()

A method which will raise an exception if the installed version of NPM is
less than the version required.

Arguments:

- `version_required`: a tuple containing the minimum version required.

```python
from django_node import npm

npm_version_required = (2, 0, 0)

npm.ensure_version_gte(npm_version_required)
```

### django_node.npm.is_installed

A boolean indicating if NPM is installed.

### django_node.npm.version

A tuple containing the version of NPM installed. For example, `(2, 0, 0)`

### django_node.npm.version_raw

A string containing the raw version returned from NPM. For example, `'2.0.0'`


Settings
--------

Settings can be overridden by defining a dictionary named `DJANGO_NODE` in your settings file.

```python
# Example

DJANGO_NODE = {
    'PATH_TO_NODE': '/path/to/some/binary',
}
```

### DJANGO_NODE['PATH_TO_NODE']

A path that will resolve to Node.js.

Default:
```python
'node'
```

### DJANGO_NODE['NODE_VERSION_COMMAND']

The command invoked on Node.js to retrieve its version.

Default:
```python
'--version'
```

### DJANGO_NODE['NODE_VERSION_FILTER']

A function which will generate a tuple of version numbers from
the raw version string returned from Node.js.

Default
```python
lambda version: tuple(map(int, (version[1:] if version[0] == 'v' else version).split('.')))
```

### DJANGO_NODE['PATH_TO_NPM']

A path that will resolve to NPM.

Default
```python
'npm'
```

### DJANGO_NODE['NPM_VERSION_COMMAND']

The command invoked on NPM to retrieve its version.

Default
```python
'--version'
```

### DJANGO_NODE['NPM_VERSION_FILTER']

A function which will generate a tuple of version numbers from
the raw version string returned from NPM.

Default
```python
lambda version: tuple(map(int, version.split('.'))),
```

### DJANGO_NODE['NPM_INSTALL_COMMAND']

The install command invoked on NPM. This is prepended to all calls to `django_node.npm.install`.

Default
```python
'install'
```

### DJANGO_NODE['NPM_INSTALL_PATH_TO_PYTHON']

A path to a python interpreter which will be provided by NPM to any dependencies which require
Python.

If you are using Python 3 as your system default or virtualenv `python`, NPM may throw errors
while installing certain libraries - such as `gyp` - which depend on Python 2.x. Specifying a
path to a Python 2.x interpreter should resolve these errors.

Default
```python
None
```


Running the tests
-----------------

```bash
mkvirtualenv django-node
pip install -r requirements.txt
python runtests.py
```
