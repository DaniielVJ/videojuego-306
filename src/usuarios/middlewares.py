from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect

class VerificarLoginMiddleware:
    
    def __init__(self, get_response=None):
        self.get_response = get_response
    

    def __call__(self, request, *args, **kwargs):
        paths_publicos = [reverse(path_name) for path_name in settings.PUBLIC_URLS_NAMES]
        if request.path in paths_publicos and request.user.is_authenticated:
            return redirect('usuarios:inicio_usuario')
        return self.get_response(request)
        