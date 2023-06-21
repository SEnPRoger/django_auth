from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import localdate
import requests
from pathlib import Path
from django.conf import settings
import datetime, time
from JWTAuth.views import JWTToken
from account.models import Account
from django.middleware import csrf

# Create your views here.
class AccountRegister(APIView):
    def post(self, request, format=None):
        serializer = AccountRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            account = serializer.save()
            
            file = request.data.get('account_photo')
            if file is not None:
                extension = str(file).split('.')[1]
            
                if extension == 'gif' and request.user.is_moderator == False:
                    return Response({'error':'you cannot upload gif as account photo'},
                                    status=status.HTTP_403_FORBIDDEN)
            else:
                account.account_photo = file
                account.save()

            user = authenticate(request, username=account.nickname, password=request.data.get('password'))
            if user is not None:
                login(request, user)
            else:
                return Response({'error': 'Unable to authenticate user'},
                                status=status.HTTP_400_BAD_REQUEST)
            
            refresh_token, access_token = JWTToken.generate_tokens(user_id=account.id)
            response = Response({'access_token':access_token,
                                 'nickname':account.nickname},
                                status=status.HTTP_200_OK)
            JWTToken.set_refresh_to_header(response, refresh_token, header_name='refresh-token')
            response['X-CSRFToken'] = csrf.get_token(request)
                
            return response
        else:
            return Response({'error':serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
        
class AccountLogin(APIView):
    def post(self, request, format=None):
        serializer = AccountLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            nickname_or_email = serializer.data.get('nickname_or_email')
            password = serializer.data.get('password')

            account = authenticate(request, username=nickname_or_email, password=password)
            if account is not None:
                login(request, account)
                refresh_token, access_token = JWTToken.generate_tokens(user_id=account.id)
                response = Response({'access_token':access_token,
                                     'nickname':account.nickname},
                                    status=status.HTTP_200_OK)
                JWTToken.set_refresh_to_header(response, refresh_token, header_name='refresh-token')
                response['X-CSRFToken'] = csrf.get_token(request)
                return response
            else:
                return Response({'status':'account not found!'},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error':serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
        
class AccountView(APIView):
    def get(self, request, nickname=None, format=None):
        try:
            account = Account.objects.get(nickname=nickname)
            if request.user.is_authenticated:
                if account.blocked_accounts.filter(id=request.user.id).exists():
                    return Response(
                        {'detail': 'you have been blocked by the owner of the account'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                profile_nickname = request.user.nickname
            else:
                profile_nickname = None
            serializer = AccountGetPublic(account)
        except ObjectDoesNotExist:
            return Response({'detail':'profile not found'},
                             status=status.HTTP_200_OK)
        return Response({'data':serializer.data,
                             'profile':profile_nickname},
                             status=status.HTTP_200_OK)

class AccountPrivateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = AccountGetPrivate(request.user)
        response = Response({'data':serializer.data},
                            status=status.HTTP_200_OK)
        
        response['X-CSRFToken'] = csrf.get_token(request)
        return response