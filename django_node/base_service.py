import os
from django.utils import six
if six.PY2:
    from urlparse import urljoin
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse
    from urllib.parse import urljoin
from .exceptions import ServiceSourceDoesNotExist, MalformedServiceName, ServerConfigMissingService, NodeServiceError
from .settings import SERVICE_TIMEOUT
from .utils import convert_html_to_plain_text


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
        if urlparse(name).netloc or not name.startswith('/') or name == '/':
            raise MalformedServiceName(name)

    @classmethod
    def get_name(cls):
        if cls.name is not None:
            return cls.name

        python_path = '{module_path}.{class_name}'.format(
            module_path=cls.__module__,
            class_name=cls.__name__,
        )

        cls.name = urljoin('/', python_path.replace('.', '/'))

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

    def handle_response(self, response):
        if response.status_code != 200:
            error_message = convert_html_to_plain_text(response.text)
            message = 'Error at {name}: {error_message}'
            raise NodeServiceError(message.format(
                name=self.get_name(),
                error_message=error_message,
            ))
        return response

    def ensure_loaded(self):
        if self.__class__ not in self.get_server().services:
            raise ServerConfigMissingService(self.__class__)

    def send(self, **kwargs):
        self.ensure_loaded()

        response = self.server.get_service(
            self.get_name(),
            timeout=self.timeout,
            params=kwargs
        )

        return self.handle_response(response)