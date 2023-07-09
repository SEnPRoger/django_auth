from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from account.models import *
from django.middleware import csrf
from rest_framework.parsers import MultiPartParser
from django.core.signing import Signer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import base36
import shortuuid
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import generics
from rest_framework.decorators import action, permission_classes
from rest_framework.viewsets import ModelViewSet

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

            # if authenticated user is a owner of searching account - give him a private info about his account
            if request.user.is_authenticated and request.user.nickname == nickname:
                serializer = AccountGetPrivate(account)
            else:
                serializer = AccountGetPublic(account)

        except ObjectDoesNotExist:
            similar_records = self.find_similar_nickname(nickname)

            if similar_records.count() != 0:
                serializer = AccountSimilar(similar_records, many=True)
                return Response({'similar_accounts': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'account doesn`t exist'},
                            status=status.HTTP_404_NOT_FOUND)
            
        response = Response({'data':serializer.data,
                             'profile':profile_nickname},
                             status=status.HTTP_200_OK)
        response['X-CSRFToken'] = csrf.get_token(request)
        return response
    
    def find_similar_nickname(self, nickname):
        similarity_value = 0.3 # if value a < 0.3 < b, where a - closer to input data, where b - more wide range of search
        similar_nicknames = Account.objects.annotate(similarity=TrigramSimilarity('nickname', nickname)).filter(similarity__gt=similarity_value).order_by('-similarity')
        return similar_nicknames
    
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
        try:
            old_code = VerificationCode.objects.get(email=email)
            old_code.code = short_encoded_data
            old_code.save()
        except ObjectDoesNotExist:
            new_code = VerificationCode.objects.create(email=email, code=short_encoded_data)

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
        email = request.data.get('email')
        code = request.data.get('code')

        # searching for requested new user by nickname

        verification_code = VerificationCode.objects.get(email=email)

        if verification_code is not None:

            # and comparing with encoded data which was passed from email
            if verification_code.code == code:
                verification_code.delete()
                response = Response({'detail':'Email has been verified'},
                                    status=status.HTTP_200_OK)
                return response
            else:
                # if user actually sent a request but typed a wrong code
                response = Response({'detail':'Invalid verification code'},
                                    status=status.HTTP_400_BAD_REQUEST)
                return response
        else:
            response = Response({'detail':'Requested user doesn`t sent any request to confirm email'},
                                    status=status.HTTP_404_NOT_FOUND)
            return response
        
class AccountEdit(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = AccountUpdateInfoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            account = Account.objects.get(id=request.user.id)
            
            keys_to_exclude = ['account_photo', 'account_banner']
            for key, value in serializer.validated_data.items():
                if key not in keys_to_exclude:
                    setattr(account, key, value)
            account.save()

            photo = request.FILES.get('account_photo')
            banner = request.FILES.get('account_banner')
            extension = str(photo).split('.')[1]
            extension2 = str(banner).split('.')[1]
            
            if extension == 'gif' and request.user.is_moderator == False or extension2 == 'gif' and request.user.is_moderator:
                return Response({'detail':'you cannot upload gif as account photo'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                account = Account.objects.get(id=request.user.id)
                if account.account_photo != None:
                    account.account_photo.delete()
                account.account_photo = photo
                if account.account_banner != None:
                    account.account_banner.delete()
                account.account_banner = banner
                account.save()

            response = Response({'detail':'account has been updated'},
                                status=status.HTTP_200_OK)
            return response
        else:
            response = Response({'detail':'something went wrong'},
                                status=status.HTTP_400_BAD_REQUEST)
            return response

class AccountBlockedListViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer = AccountBlockedSerializer

    @action(methods=['get'], detail=False)
    @permission_classes([IsAuthenticated])
    def get_blocked_accounts(self, request):
        blocked_accounts = request.user.blocked_accounts.all()

        if blocked_accounts.count() > 0:
            serializer = AccountBlockedSerializer(blocked_accounts, many=True, context={'request': request})
            response = Response({'amount':blocked_accounts.count(),
                                 'blocked_accounts': serializer.data},
                                status=status.HTTP_200_OK)
            return response
        else:
            response = Response({'detail': 'account does not have any blocked accounts'},
                                status=status.HTTP_200_OK)
            return response
    
    @action(methods=['post'], detail=True)
    @permission_classes([IsAuthenticated])
    def add_blocked_account(self, request, nickname=None):
        try:
            account_to_block = Account.objects.get(nickname=nickname)
        except ObjectDoesNotExist:
            response = Response({'detail':"account does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            return response
        
        request.user.blocked_accounts.add(account_to_block)
        response = Response({'detail':'account was added to blocked list'},
                                status=status.HTTP_200_OK)
        return response
    
    @action(methods=['post'], detail=True)
    @permission_classes([IsAuthenticated])
    def remove_blocked_account(self, request, nickname=None):
        try:
            account_to_block = Account.objects.get(nickname=nickname)
        except ObjectDoesNotExist:
            response = Response({'detail':"account does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            return response
        
        request.user.blocked_accounts.remove(account_to_block)
        response = Response({'detail':'account was removed from blocked list'},
                                status=status.HTTP_200_OK)
        return response

class AccountDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, nickname, format=None):
        try:
            account = Account.objects.get(nickname=request.user.nickname)
        except ObjectDoesNotExist:
            response = Response({'detail':"account does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            return response
        
        if request.user.nickname == account.nickname or request.user.is_moderator:
            account.delete()
            response = Response({'detail':'account was deleted'},
                                    status=status.HTTP_200_OK)
            return response
        else:
            response = Response({'detail':'you cannot delete account'},
                                    status=status.HTTP_403_FORBIDDEN)
            return response

class AccountVerifyViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer = AccountVerifySerializer

    @action(methods=['get'], detail=True)
    @permission_classes([AllowAny])
    def get_request(self, request, request_id=None):
        try:
            verify_request = VerifiedAccount.objects.get(id=request_id)
        except ObjectDoesNotExist:
            response = Response({'detail':"does not exist"},
                                status=status.HTTP_200_OK)
            return response
        response = Response({'changed_date':verify_request.changed_date},
                                status=status.HTTP_200_OK)
        return response
    
    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def add_request(self, request):
        serializer = AccountVerifySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            if request.user.is_blocked != True:
                serializer.create_request()
                response = Response({'detail':'verify request has been sent'},
                                    status=status.HTTP_200_OK)
                return response
            else:
                response = Response({'detail':'you cannot send a verify request'},
                                status=status.HTTP_400_BAD_REQUEST)
                return response
            
    @action(methods=['post'], detail=True)
    @permission_classes([IsAuthenticated])
    def change_request(self, request, request_id=None):
        serializer = AccountVerifySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                verify_request = VerifiedAccount.objects.get(id=request_id)
            except ObjectDoesNotExist:
                response = Response({'detail':'verify request not found'},
                                        status=status.HTTP_200_OK)
                return response
        
            account = verify_request.account
            verify_status = serializer.validated_data.get('is_verified')

            if request.user.is_moderator:
                if verify_request.account != request.user:
                    if verify_status == True:
                        verify_request.is_verified = True
                        verify_request.provided_by = request.user
                        verify_request.changed_date = datetime.datetime.now()
                        account.is_verify = True
                        account.save()
                        verify_request.save()
                    else:
                        account.is_verify = False
                        account.save()
                        verify_request.delete()
                    response = Response({'detail':'verify request has been changed'},
                                    status=status.HTTP_200_OK)
                    return response
                else:
                    response = Response({'detail':'you cannot change your own request'},
                                    status=status.HTTP_400_BAD_REQUEST)
                    return response
            else:
                response = Response({'detail':'you cannot change a verify status'},
                                status=status.HTTP_400_BAD_REQUEST)
                return response