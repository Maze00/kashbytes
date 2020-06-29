from django.shortcuts import redirect
from django.urls import resolve
from django.conf import settings


class CheckAdminIsAuthenticated:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(request.path_info).url_name
        if(url_name in settings.PROTECTED_URL_NAMES) and not request.user.is_authenticated:
            response = redirect('user_login')
        else:
            response = self.get_response(request)
        return response
