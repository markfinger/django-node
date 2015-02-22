django_node.npm
===============

The `django_node.npm` module provides utils for introspecting and calling [NPM](https://www.npmjs.com/).

Methods
- [django_node.npm.install()](#django_nodenpminstall)
- [django_node.npm.run()](#django_nodenpmrun)
- [django_node.npm.ensure_installed()](#django_nodenpmensure_installed)
- [django_node.npm.ensure_version_gte()](#django_nodenpmensure_version_gte)

Attributes
- [django_node.npm.is_installed](#django_nodenpmis_installed)
- [django_node.npm.version](#django_nodenpmversion)
- [django_node.npm.version_raw](#django_nodenpmversion_raw)

### django_node.npm.install()

Invokes NPM's install command in a specified directory.

Arguments:

- `target_dir`: a string pointing to the directory which the command will be invoked in.

```python
from django_node import npm

# Install the dependencies in a particular directory
npm.install('/path/to/some/directory/')
```

### django_node.npm.run()

Invokes NPM with the arguments provided and returns the resulting stderr and stdout.

```python
from django_node import npm

stderr, stdout = npm.run('install', '--save', 'some-package')
```

### django_node.npm.ensure_installed()

Raises an exception if NPM is not installed.

### django_node.npm.ensure_version_gte()

Raises an exception if the installed version of NPM is less than the version required.

Arguments:

- `version_required`: a tuple containing the minimum version required.

```python
from django_node import npm

npm.ensure_version_gte((2, 0, 0,))
```

### django_node.npm.is_installed

A boolean indicating if NPM is installed.

### django_node.npm.version

A tuple containing the version of NPM installed. For example, `(2, 0, 0)`

### django_node.npm.version_raw

A string containing the raw version returned from NPM. For example, `'2.0.0'`