import inspect
from .settings import SERVER
from .utils import dynamic_import_attribute

# Allow the server to be configurable
server = dynamic_import_attribute(SERVER)
if inspect.isclass(server):
    server = server()