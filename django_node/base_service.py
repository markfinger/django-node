import os
from django.utils import six
if six.PY2:
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse
from .exceptions import ServiceSourceDoesNotExist, MalformedServiceName, ServerConfigMissingService
from .settings import SERVICE_TIMEOUT


class BaseService(object):
    path_to_source = None
    name = None
    server = None
    timeout = SERVICE_TIMEOUT

    @classmethod
    def validate(cls):
        path_to_source = cls.get_path_to_source()
        if not path_to_source or not os.path.exists(path_to_source):
            raise ServiceSourceDoesNotExist(cls.get_path_to_source())

        # Ensure that the name is a relative url starting with `/`
        name = cls.get_name()
        if urlparse(name).netloc or not name.startswith('/'):
            raise MalformedServiceName(name)

    @classmethod
    def get_name(cls):
        if cls.name is not None:
            return cls.name

        python_path = '{module_path}.{class_name}'.format(
            module_path=cls.__module__,
            class_name=cls.__name__,
        )

        cls.name = '/{url}'.format(
            url=python_path.replace('.', '/')
        )

        return cls.name

    @classmethod
    def get_path_to_source(cls):
        return cls.path_to_source

    def get_server(self):
        if self.server is not None:
            return self.server

        from .server import server
        self.server = server

        return self.server

    def send(self, **kwargs):
        server = self.get_server()

        if self.__class__ not in server.services:
            raise ServerConfigMissingService(self.__class__)

        return self.server.get_service(
            self.get_name(),
            timeout=self.timeout,
            params=kwargs
        )