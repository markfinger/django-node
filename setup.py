from setuptools import setup, find_packages

VERSION = '4.0.0'

setup(
    name='django-node',
    version=VERSION,
    packages=find_packages(exclude=('tests', 'example',)),
    package_data={
        'django_node': [
            'node_server.js',
            'services/echo.js',
            'package.json',
        ],
    },
    install_requires=[
        'django',
        'requests>=2.5.1',
    ],
    description='Bindings and utils for integrating Node.js and NPM into a Django application',
    long_description='Documentation at https://github.com/markfinger/django-node',
    author='Mark Finger',
    author_email='markfinger@gmail.com',
    url='https://github.com/markfinger/django-node',
)
