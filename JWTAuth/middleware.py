from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework import status

class UserCookieMiddleWare(MiddlewareMixin):
    """
    Middleware to set user cookie
    If user is authenticated and there is no cookie, set the cookie,
    If the user is not authenticated and the cookie remains, delete it
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        from rest_framework.renderers import JSONRenderer
        from JWTAuth.views import JWTToken
        
        if request.COOKIES.get('refresh_cookie'):
            try:
                raw_refresh_token = JWTToken.get_refresh_token(request, cookie_name='refresh_cookie')
                raw_access_token = JWTToken.get_access_token(request)
                
                if JWTToken.validate(raw_access_token) != True:
                    if JWTToken.validate(raw_refresh_token):
                        refresh_token, access_token = JWTToken.generate_tokens(JWTToken.get_userid(raw_refresh_token))
                        response = Response(
                            data={'status':'Access token is not valid',
                                  'detail':'Token has expired or incorrect',
                                  'access_token':access_token},
                                  status=status.HTTP_401_UNAUTHORIZED
                        )
                        response.accepted_renderer = JSONRenderer()
                        response.accepted_media_type = "application/json"
                        response.renderer_context = {}

                        JWTToken.set_refresh_to_cookie(response, refresh_token, cookie_name='refresh_cookie')
                        
                        response['X-CSRFToken'] = request.COOKIES.get('X-CSRFToken')
                        return response
                    else:
                        response = Response(
                            data={'status':'Refresh token is not valid',
                                  'detail':'Token has expired or incorrect'},
                                  status=status.HTTP_401_UNAUTHORIZED
                        )
                        response.accepted_renderer = JSONRenderer()
                        response.accepted_media_type = "application/json"
                        response.renderer_context = {}

                        response.delete_cookie("refresh_cookie")
                        response.delete_cookie('X-CSRFToken')
                        return response
            except AttributeError:
                pass