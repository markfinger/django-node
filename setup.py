from setuptools import setup

VERSION = '1.0.0'

setup(
    name='django-node',
    version=VERSION,
    packages=['django_node'],
    install_requires=['django'],
    description='Django Node',
    long_description=\
'''
Bindings and utils for integrating Node.js and NPM into a Django application.

Documentation at https://github.com/markfinger/django-node
''',
    author='Mark Finger',
    author_email='markfinger@gmail.com',
    url='https://github.com/markfinger/django-node',
)