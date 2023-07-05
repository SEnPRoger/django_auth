from account.views import *
from django.urls import path, include

app_name = "account"

urlpatterns = [
    path('register/', AccountRegister.as_view(), name='register'),
    path('login/', AccountLogin.as_view(), name='login'),

    path('send_email_code/', AccountSendEmailCode.as_view(), name='send_email_code'),
    path('confirm_email/', AccountConfirmEmail.as_view(), name='confirm_email'),

    path('get_verify_request/', AccountGetVerify.as_view(), name='get_verify_request'),
    path('send_verify_request/', AccountSendVerifyRequest.as_view(), name='send_verify_request'),
    path('change_verify_request/<int:id>/', AccountChangeVerify.as_view(), name='change_verify_request'),

    path('upload_photo/', AccountPhotoUpload.as_view(), name='upload_photo'),
    path('upload_banner/', AccountBannerUpload.as_view(), name='upload_banner'),

    path('update_public_info/', AccountUpdateInfo.as_view(), name='update_public_info'),

    path('private/', AccountPrivateView.as_view(), name='private_view'),
    path('<str:nickname>/', AccountView.as_view(), name='view'),

    path('check_nickname/<str:nickname>/', CheckNicknameAvailable.as_view(), name='check_nickname'),
    path('check_email/<str:email>/', CheckEmailAvailable.as_view(), name='check_email'),
]