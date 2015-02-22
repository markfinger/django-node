django_node.node
================

The `django_node.node` module provides utils for introspecting and calling [Node](http://nodejs.org/).

Methods
- [django_node.node.run()](#django_nodenoderun)
- [django_node.node.ensure_installed()](#django_nodenodeensure_installed)
- [django_node.node.ensure_version_gte()](#django_nodenodeensure_version_gte)

Attributes
- [django_node.node.is_installed](#django_nodenodeis_installed)
- [django_node.node.version](#django_nodenodeversion)
- [django_node.node.version_raw](#django_nodenodeversion_raw)


### django_node.node.run()

Invokes Node with the arguments provided and return the resulting stderr and stdout.

Accepts an optional keyword argument, `production`, which will ensure that the command is run
with the `NODE_ENV` environment variable set to 'production'.

```python
from django_node import node

stderr, stdout = node.run('/path/to/some/file.js', '--some-argument')

# With NODE_ENV set to production
stderr, stdout = node.run('/path/to/some/file.js', '--some-argument', production=True)
```

### django_node.node.ensure_installed()

Raises an exception if Node is not installed.

### django_node.node.ensure_version_gte()

Raises an exception if the installed version of Node is less than the version required.

Arguments:

`version_required`: a tuple containing the minimum version required.

```python
from django_node import node

node.ensure_version_gte((0, 10, 0,))
```

### django_node.node.is_installed

A boolean indicating if Node.js is installed.

### django_node.node.version

A tuple containing the version of Node.js installed. For example, `(0, 10, 33)`

### django_node.node.version_raw

A string containing the raw version returned from Node.js. For example, `'v0.10.33'`
