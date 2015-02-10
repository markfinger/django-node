import inspect
from .settings import SERVER
from .utils import dynamic_import

# Allow the server to be configurable
server = dynamic_import(SERVER)
if inspect.isclass(server):
    server = server()