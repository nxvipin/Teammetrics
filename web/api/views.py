from django.http import HttpResponse

def index(request, api_version):
    return HttpResponse("Test")
