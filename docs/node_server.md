Node Server
===========

The `django_node.node_server` module provides an interface, `NodeServer`, for interacting
with a JS service host such as 
[django-node-server](https://github.com/markfinger/django-node-server). In practice,
you will rarely need to interact with the server itself, rather you should use
django-node's [JS services](js_services.md).

django-node opens up a singleton instance of `NodeServer` via the `django_node.server`
module.

```
from django_node.server import server

# Test if the server is running
server.test()
```

If you wish to change the behaviour of the server singleton, you can change the 
`DJANGO_NODE['SERVER']` setting to a dotstring pointing to your server class, which
will be imported at runtime.
