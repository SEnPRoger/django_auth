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
from account.models import Account, VerificationCode
from django.middleware import csrf
from rest_framework.parsers import MultiPartParser
from django.core.signing import Signer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import base36
import shortuuid

# Create your views here.
class AccountRegister(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        serializer = AccountRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            account = serializer.save()
            
            file = request.FILES.get('account_photo')
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
    
class CheckNicknameAvailable(APIView):
    def get(self, request, nickname=None, format=None):
        try:
            account = Account.objects.get(nickname=nickname)
            if account is not None:
                response = Response({"result":"nickname is already occupied"}, status=status.HTTP_400_BAD_REQUEST)
                return response
        except ObjectDoesNotExist:
            response = Response({"result":"nickname is free"}, status=status.HTTP_200_OK)
            return response
        
class CheckEmailAvailable(APIView):
    def get(self, request, email=None, format=None):
        try:
            account = Account.objects.get(email=email)
            if account is not None:
                response = Response({"result":"email is already occupied"}, status=status.HTTP_400_BAD_REQUEST)
                return response
        except ObjectDoesNotExist:
            response = Response({"result":"email is free"}, status=status.HTTP_200_OK)
            return response
        
class AccountPhotoUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountPhotoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            file = request.FILES.get('photo')
            extension = str(file).split('.')[1]
            
            if extension == 'gif' and request.user.is_moderator == False:
                return Response({'detail':'you cannot upload gif as account photo'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                account = Account.objects.get(id=request.user.id)
                if account.account_photo != None:
                    account.account_photo.delete()
                account.account_photo = file
                account.save()

                return Response({'detail':'successfully uploaded photo'},
                                    status=status.HTTP_200_OK)
        else:
            response = Response({'detail':serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            return response
        
class AccountBannerUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountPhotoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            file = request.FILES.get('photo')
            extension = str(file).split('.')[1]
            
            if extension == 'gif' and request.user.is_moderator == False:
                return Response({'detail':'you cannot upload gif as account banner'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                account = Account.objects.get(id=request.user.id)
                if account.account_banner != None:
                    account.account_banner.delete()
                account.account_banner = file
                account.save()

                return Response({'detail':'successfully uploaded banner'},
                                    status=status.HTTP_200_OK)
        else:
            response = Response({'detail':serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            return response

class AccountSendEmailCode(APIView):
    def post(self, request):

        # getting input unique data from new user
        email = request.data.get('email')

        # signing a secret code using unique data
        signer = Signer()
        signed_data = signer.sign(str(email) + str(timezone.now()))
        encoded_data = base36.dumps(int.from_bytes(signed_data.encode(), 'big'))
        short_encoded_data = shortuuid.uuid(name=encoded_data)[:6]

        # storing a planning nickname and create code date into db
        verification_code = VerificationCode.objects.create(email=email, code=short_encoded_data)

        context = {'verification_code': short_encoded_data}
        html_message = render_to_string('verify_email.html', context)
        plain_message = strip_tags(html_message)

        # sending a email with secret code
        send_mail(
            'Verification code',
            plain_message,
            'noreply@example.com',
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        response = Response({'detail':'Verification code has been sent to email'},
                                status=status.HTTP_200_OK)
        return response

class AccountConfirmEmail(APIView):
    def post(self, request):

        # getting a nickname and secret code for checking
        email = request.POST.get('email')
        code = request.POST.get('code')

        # searching for requested new user by nickname
        verification_code = VerificationCode.objects.filter(email=email).order_by('-created_date').first()

        if verification_code is not None:

            # and comparing with encoded data which was passed from email
            if verification_code.code == code:
                verification_code.delete()
                response = Response({'detail':'Email has been verified'},
                                    status=status.HTTP_200_OK)
                return response
            else:
                # if user actually sent a request but typed a wrong code - delete record to generate a new one
                if email == verification_code.email:
                    verification_code.delete()
                response = Response({'detail':'Invalid verification code'},
                                    status=status.HTTP_400_BAD_REQUEST)
                return response
        else:
            response = Response({'detail':'Requested user doesn`t sent any request to confirm email'},
                                    status=status.HTTP_404_NOT_FOUND)
            return response