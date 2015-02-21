Django Node Example
===================

The example project illustrates a simple way to integrate server-side
execution of JS into a Python process.

The relevant parts are:
- [djangosite/services/hello_world.js](djangosite/services/hello_world.js) - your JS service which takes in data and returns a response
- [djangosite/services.py](djangosite/services.py) - a python interface to your JS service
- [djangosite/views.py](djangosite/views.py) - sending data to your service and rendering the output

The following settings inform django-node to load the specific services into the node server.

```python
INSTALLED_APPS = (
    # ...
    'django_node',
)

# ...

DJANGO_NODE = {
    'SERVICES': (
        'djangosite.services',
    )
}
```

Running the example
-------------------

```bash
cd django-node/example
mkvirtualenv django-node-example
pip install -r requirements.txt
./manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser.
