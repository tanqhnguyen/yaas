from django.http import HttpResponse
from django.utils import simplejson

def json_response(data):
    json_data = simplejson.dumps(data)
    return HttpResponse(json_data, content_type="application/json")