from django.contrib.auth import get_user_model
from rest_framework import HTTP_HEADER_ENCODING, authentication, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from .exceptions import AuthenticationFailed, InvalidToken, TokenError
from datetime import timedelta
from django.conf import settings
import jwt

settings = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=3),

    'USER_ID_CLAIM':'user_id',
    'USER_ID_FIELD': 'id',
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

class JWTAuthentication(authentication.BaseAuthentication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        from JWTAuth.views import JWTToken
        header = self.get_header(request)
        if header is None:
            return None

        raw_refresh_token = JWTToken.get_refresh_token(request, header_name='refresh_token')
        raw_access_token = JWTToken.get_access_token(request)

        if raw_access_token is None or raw_refresh_token is None:
            return None

        validated_token = self.get_validated_token(raw_refresh_token, raw_access_token)

        return self.get_user(validated_token), validated_token

    # def authenticate_header(self, request):
    #     return 'fsdfsdfsfd'
    
    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(settings.get('AUTH_HEADER_NAME'))

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header
    
    def get_user(self, validated_token):
        try:
            user_id = validated_token[settings.get('USER_ID_CLAIM')]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = self.user_model.objects.get(**{settings.get('USER_ID_FIELD'): user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user
    
    def get_validated_token(self, raw_refresh_token, raw_access_token):
        # from JWTAuth.views import JWTToken

        # if JWTToken.validate(raw_refresh_token) != True:
        #     pass
            #raise InvalidToken(_('(Refresh Token invalid) ExpiredSignatureError'))

        try:
            decoded_access = jwt.decode(raw_access_token, 'sdfsdfsdf', algorithms="HS256")
        except jwt.exceptions.ExpiredSignatureError:
            raise InvalidToken(_('(Token invalid) ExpiredSignatureError'))
        except jwt.exceptions.InvalidSignatureError:
            raise InvalidToken(_('(Token invalid) InvalidSignatureError'))
        except jwt.exceptions.DecodeError:
            raise InvalidToken(_('(Token invalid) DecodeError'))
        return decoded_access
    
