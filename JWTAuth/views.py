import jwt, time, datetime
from django.utils import timezone
from .authentication import settings

class JWTToken():
    """
    Class for working with JWT tokens
    """
    @staticmethod
    def GenerateToken(user_id, type, lifetime):
        """
        Generating token and encode information to JWT token

        Arguments:
            user_id (id from database), type (access or refresh), lifetime (period of active)

        Returns:
            token
        """
        token_lifetime = datetime.datetime.now(tz=timezone.utc) + lifetime
        token = jwt.encode({"user_id": user_id,
                                "type": type,
                                "exp": token_lifetime,
                                "time": str(JWTToken.datetime_from_utc_to_local(token_lifetime))},
                                "sdfsdfsdf", algorithm="HS256")
        return token

    @staticmethod
    def generate_tokens(user_id):
        """
        Generating refresh and access tokens (JWT encoding)

        Arguments:
            user_id (id from database)

        Returns:
            refresh_token, access_token
        """
        return JWTToken.GenerateToken(user_id, 'refresh', settings.get('REFRESH_TOKEN_LIFETIME')), JWTToken.GenerateToken(user_id, 'access', settings.get('ACCESS_TOKEN_LIFETIME'))
    
    @staticmethod
    def get_refresh_token(request, header_name):
        """
        Getting refresh token from cookies (JWT encoding)

        Arguments:
            request, cookie_name (like 'refresh_cookie')

        Returns:
            refresh_token
        """
        #return request.COOKIES.get(cookie_name)
        return request.headers[header_name]
    
    @staticmethod
    def get_access_token(request):
        """
        Getting access token from AUTHORIZATION header of request (JWT encoding)

        Arguments:
            request

        Returns:
            access_token
        """
        return request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

    @staticmethod
    def set_refresh_to_cookie(response, refresh_token, cookie_name):
        """
        Setting refresh token to cookies with httponly=True

        Arguments:
            response, refresh_token, cookie_name (like 'refresh_cookie')
        """
        response.set_cookie(key = cookie_name,
                            value = refresh_token,
                            expires = JWTToken.get_expires_date(refresh_token),
                            samesite = 'None',
                            secure = True,
                            domain = 'http://localhost:3000',
                            path = '/',
                            httponly = True)

    @staticmethod
    def set_refresh_to_header(response, refresh_token, header_name):
        response[header_name] = refresh_token

    @staticmethod
    def validate(token):
        """
        Validating JWT token

        Arguments:
            token

        Returns:
            True or False (Boolean)
        """
        try:
            decoded = jwt.decode(token, 'sdfsdfsdf', algorithms="HS256")
        except jwt.exceptions.ExpiredSignatureError:
            return False
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False
        return True
    
    @staticmethod
    def decode(token):
        decoded_token = jwt.decode(token, 'sdfsdfsdf', algorithms="HS256")
        return decoded_token
    
    @staticmethod
    def get_userid(token):
        """
        Getting user_id from payload of token

        Arguments:
            token

        Returns:
            user_id (int)
        """
        decoded_token = jwt.decode(token, 'sdfsdfsdf', algorithms="HS256")
        return decoded_token['user_id']
    
    @staticmethod
    def get_expires_date(token):
        """
        Getting token expire date

        Arguments:
            token

        Returns:
            Date of expire date (Datetime)
        """
        decoded_token = jwt.decode(token, 'sdfsdfsdf', algorithms="HS256")
        date = decoded_token['exp']
        return datetime.datetime.strftime(datetime.datetime.fromtimestamp(date), "%a, %d-%b-%Y %H:%M:%S GMT")
    
    @staticmethod
    def datetime_from_utc_to_local(utc_datetime):
        """
        Converting UTC time to readble format, as 15 September 20:30:15

        Arguments:
            utc_datetime

        Returns:
            Converted datetime to readble format (Datetime)
        """
        now_timestamp = time.time()
        offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
        return datetime.datetime.strftime(utc_datetime + offset,'%d %B %Y %H:%M:%S')