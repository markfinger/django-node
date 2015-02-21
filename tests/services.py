import os
from django_node.base_service import BaseService


class TimeoutService(BaseService):
    path_to_source = os.path.join(os.path.dirname(__file__), 'services', 'timeout.js')
    timeout = 1.0


class ErrorService(BaseService):
    path_to_source = os.path.join(os.path.dirname(__file__), 'services', 'error.js')