from .settings import SERVER
from django_node.exceptions import ServerInterfaceMissingEndpoints
from .utils import dynamic_import


class ServerInterface(object):
    server = None
    root_url = None
    endpoints = None

    def __init__(self):
        if self.server is None:
            server_callable = dynamic_import(SERVER)
            self.server = server_callable()

        if not self.endpoints:
            raise ServerInterfaceMissingEndpoints(self)

        for endpoint in self.endpoints:
            self.register_endpoint(
                self.get_url_to_endpoint(endpoint['url']),
                endpoint['path_to_source'],
            )

    def get_url_to_endpoint(self, endpoint):
        if self.root_url is not None:
            return '{root_url}{endpoint}'.format(
                root_url=self.root_url,
                endpoint=endpoint,
            )
        return endpoint

    def register_endpoint(self, url, path_to_source):
        return self.server.register_endpoint(url, path_to_source)

    def get(self, endpoint, params):
        url = self.get_url_to_endpoint(endpoint)
        return self.server.get(url, params=params)