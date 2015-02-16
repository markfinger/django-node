Django Node Example
===================

The example project illustrates a simple way to integrate serverside
execution of JS a Python process.

The relevant parts are:
- [djangosite/views.py](djangosite/views.py)
- [djangosite/hello_world.js](djangosite/hello_world.js)

Running the example
-------------------

```bash
cd django-node/example
mkvirtualenv django-node-example
pip install -r requirements.txt
./manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser.
