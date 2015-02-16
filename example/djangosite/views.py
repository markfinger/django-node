import os
from django.http import HttpResponse
from django_node.server import server


hello_world_service = server.add_service(
    '/hello-world',
    os.path.join(os.path.dirname(__file__), 'hello_world.js')
)


def hello_world(request):
    content = hello_world_service(name='World')
    return HttpResponse(content)