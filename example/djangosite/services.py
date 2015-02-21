import os
from django_node.base_service import BaseService


class HelloWorldService(BaseService):
    path_to_source = os.path.join(os.path.dirname(__file__), 'services', 'hello_world.js')