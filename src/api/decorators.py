from django.contrib.auth import authenticate
from core.utils import json_response
from django.utils.translation import ugettext_lazy as _

def api_authentication(*args, **kwargs):
    def decorator(function):
        def inner(request, *args, **kwargs):
            # for demonstration purpose, use plain username/password
            # in reality, this should be an API key or key/secret
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                request.user = user
                return function(request, *args, **kwargs)
            else:
                return json_response({'error': _('Invalid account')})
        return inner
    return decorator