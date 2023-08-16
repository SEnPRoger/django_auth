from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from account.models import Account, Token

class UserHeaderMiddleWare(MiddlewareMixin):
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
        
        try:
            # here we are getting raw access & refresh tokens
            raw_refresh_token = JWTToken.get_refresh_token(request, header_name='refresh-token')
            raw_access_token = JWTToken.get_access_token(request)

            # then we decoding recieved refresh token and getting nickname and UUID
            account_nickname = JWTToken.get_nickname(raw_refresh_token, request)
            account_uuid = JWTToken.get_uuid(raw_refresh_token)

            # after we are trying to find UUID among other tokens
            try:
                current_token = Token.objects.get(uuid=account_uuid)
            # if we can not find it - it means that token was not created or its no longer available to use
            except ObjectDoesNotExist:
                return Response('Current refresh token is not available to use')

            # otherwise we are validating tokens by checking theirs expires dates
            # if access token is not valid
            if JWTToken.validate(raw_access_token) == False:
                
                # we are checking - if refresh token is still fresh
                if JWTToken.validate(raw_refresh_token):
                    refresh_token, access_token = JWTToken.generate_tokens(JWTToken.get_userid(raw_refresh_token),
                                                                                      JWTToken.get_nickname(raw_refresh_token, request))
                    current_token.delete()

                    uuid = JWTToken.get_uuid(refresh_token)
                    account = Account.objects.get(nickname=account_nickname)
                    new_token = Token.objects.create(account=account, uuid=uuid)

                    response = Response(
                        data={
                                'status':'Access token is not valid',
                                'detail':'Token has expired or incorrect',
                                'access_token':access_token
                                },
                                status=status.HTTP_405_METHOD_NOT_ALLOWED
                    )
                    response.accepted_renderer = JSONRenderer()
                    response.accepted_media_type = "application/json"
                    response.renderer_context = {}

                    JWTToken.set_refresh_to_header(response, refresh_token, header_name='refresh-token')
                        
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

                    response.delete_cookie('X-CSRFToken')
                    return response
        except KeyError:
            pass
        except AttributeError:
            pass