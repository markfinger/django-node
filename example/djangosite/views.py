from django.http import HttpResponse
from .services import HelloWorldService

hello_world_service = HelloWorldService()


def hello_world(request):
    content = hello_world_service.greet('World')
    return HttpResponse(content)