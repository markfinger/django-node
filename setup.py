from setuptools import setup

VERSION = '0.1.0'

setup(
    name='django-node',
    version=VERSION,
    packages=['django_node'],
    install_requires=['django'],
    description='Django Node',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    author='Mark Finger',
    author_email='markfinger@gmail.com',
    url='https://github.com/markfinger/django-node',
)