Django Node Example
===================

The example project illustrates a simple way to integrate server-side
execution of JS into a Python process.

The relevant parts are:
- [djangosite/services.py](djangosite/services.py) - a python interface to your JS service
- [djangosite/views.py](djangosite/views.py) - sending data to your service
- [djangosite/services/hello_world.js](djangosite/services/hello_world.js) - the JS service which handles your data

Beyond those files, you should add django-node to django list of apps.

```python
INSTALLED_APPS = (
    # ...
    'django_node',
)
```

You will also need to point django-node at the module containing your services.

```python
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
