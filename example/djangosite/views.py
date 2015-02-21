from django.http import HttpResponse
from .services import HelloWorldService

hello_world_service = HelloWorldService()


def hello_world(request):
    response = hello_world_service.send(
        name='World'
    )
    return HttpResponse(response.text)