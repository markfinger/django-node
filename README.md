Django Node
===========

[![Build Status](https://travis-ci.org/markfinger/django-node.svg?branch=master)](https://travis-ci.org/markfinger/django-node)

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
- [NodeServer](#nodeserver)
- [Node](#node)
- [NPM](#npm)
- [Settings](#settings)
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


Running the tests
-----------------

```bash
mkvirtualenv django-node
pip install -r requirements.txt
python runtests.py
```
