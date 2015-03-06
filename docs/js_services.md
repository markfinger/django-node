JS services
===========

JS services operate under a request/response pattern, whereby the python process sends
a request to a service and will wait until the service has responded.

**TODO**
- sending data to services (kwargs to BaseService.send)
- exporting the service as a CommonJS module
- how to access node's ecosystem (call django_node.npm.install when defining your services)
