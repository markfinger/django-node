Django Node
===========

[![Build Status](https://travis-ci.org/markfinger/django-node.svg?branch=master)](https://travis-ci.org/markfinger/django-node)

django-node provides hosted JS services, bindings, and utilities which enable
you to integrate Node and NPM into a Django application.

Documentation
-------------

- [Basic usage](#basic-usage)
- [Installation](#installation)
- [JS services](docs/js_services.md)
- [NodeServer](docs/node_server.md)
- [Node](docs/node.md)
- [NPM](docs/npm.md)
- [Settings](docs/settings.md)
- [Running the tests](#running-the-tests)


Basic usage
-----------

```javascript
var service = function(request, response) {
	var name = request.query.name;
	response.send(
	    'Hello, ' + name + '!';
	);
};

module.exports = service;
```

```python
from django_node.base_service import BaseService

class HelloWorldService(BaseService):
    # An absolute path to a file containing the above JS
    path_to_source = '/path/to/file.js'

    def greet(self, name):
        response = self.send(name=name)
        return response.text

hello_world_service = HelloWorldService()

print(hello_world_service.greet('World'))  # prints 'Hello, World!'
```

You can also invoke Node and NPM directly.

```python
from django_node import node, npm

# Run a particular file with Node.js
stderr, stdout = node.run('/path/to/some/file.js', '--some-argument', 'some_value')

# Call `npm install` within a particular directory
stderr, stdout = npm.install('/path/to/some/directory')
```


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

If you wish to use JS services, you will also need to inform configure django-node 
to use your services.

```python
# in settings.py

DJANGO_NODE = {
    'SERVICES': (
        'some_app.services',
        # During initialisation django-node will import some_app/services.py and load in 
        # all the services which inherit from django_node.base_service.BaseService.
    )
}
```


Running the tests
-----------------

```bash
mkvirtualenv django-node
pip install -r requirements.txt
python runtests.py
```
