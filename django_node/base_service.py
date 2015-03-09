import os
import warnings
import json
from django.utils import six
if six.PY2:
    from urlparse import urljoin
    from urlparse import urlparse
elif six.PY3:
    from urllib.parse import urlparse
    from urllib.parse import urljoin
from .exceptions import ServiceSourceDoesNotExist, MalformedServiceName, ServerConfigMissingService, NodeServiceError
from .settings import SERVICES, SERVICE_TIMEOUT
from .utils import convert_html_to_plain_text
from .package_dependent import PackageDependent


class BaseService(PackageDependent):
    path_to_source = None
    name = None
    server = None
    timeout = SERVICE_TIMEOUT

    def __init__(self):
        self.warn_if_not_configured()

    @classmethod
    def warn_if_not_configured(cls):
        if cls.__module__ not in SERVICES:
            service_warning = (
                '{class_name} has been instantiated, but the module "{module}" is missing from '
                'the SERVICES setting.'
            ).format(class_name=cls, module=cls.__module__)
            warnings.warn(service_warning)

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

    def get_json_decoder(self):
        return None

    def generate_cache_key(self, serialized_data, data):
        return None

    def ensure_loaded(self):
        if self.__class__ not in self.get_server().services:
            raise ServerConfigMissingService(self.__class__)

    def send(self, **kwargs):
        self.ensure_loaded()

        data = kwargs
        serialized_data = json.dumps(data, cls=self.get_json_decoder())

        response = self.server.send_request_to_service(
            self.get_name(),
            timeout=self.timeout,
            data={
                'cache_key': self.generate_cache_key(serialized_data, data),
                'data': serialized_data
            }
        )

        return self.handle_response(response)