Settings
========

Settings can be overridden by defining a dictionary named `DJANGO_NODE` in your settings file.

```python
# Example

DJANGO_NODE = {
    'PATH_TO_NODE': '/path/to/some/binary',
}
```

- [PATH_TO_NODE](#django_nodepath_to_node)
- [NODE_VERSION_COMMAND](#django_nodenode_version_command)
- [NODE_VERSION_FILTER](#django_nodenode_version_filter)
- [PATH_TO_NPM](#django_nodepath_to_npm)
- [NPM_VERSION_COMMAND](#django_nodenpm_version_command)
- [NPM_VERSION_FILTER](#django_nodenpm_version_filter)
- [NPM_INSTALL_COMMAND](#django_nodenpm_install_command)
- [NPM_INSTALL_PATH_TO_PYTHON](#django_nodenpm_install_path_to_python)

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
