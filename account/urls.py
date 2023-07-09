from account.views import *
from django.urls import path, include
from rest_framework import routers

app_name = "account"


urlpatterns = [
    path('register/', AccountRegister.as_view(), name='register'),
    path('login/', AccountLogin.as_view(), name='login'),

    path('verify/<int:request_id>/', AccountVerifyViewSet.as_view({'get': 'get_request', 'post': 'change_request'}), name='verify_get_request'),
    path('verify/add', AccountVerifyViewSet.as_view({'post': 'add_request'}), name='verify_add_request'),

    path('blocked_list/', AccountBlockedListViewSet.as_view({'get': 'get_blocked_accounts'}), name='get_blocked_accounts'),
    path('blocked_list/add/<str:nickname>/', AccountBlockedListViewSet.as_view({'post': 'add_blocked_account'}), name='add_blocked_account'),
    path('blocked_list/remove/<str:nickname>/', AccountBlockedListViewSet.as_view({'post': 'remove_blocked_account'}), name='remove_blocked_account'),

    path('send_email_code/', AccountSendEmailCode.as_view(), name='send_email_code'),
    path('confirm_email/', AccountConfirmEmail.as_view(), name='confirm_email'),

    path('upload_photo/', AccountPhotoUpload.as_view(), name='upload_photo'),
    path('upload_banner/', AccountBannerUpload.as_view(), name='upload_banner'),

    path('edit/', AccountEdit.as_view(), name='edit'),

    path('<str:nickname>/', AccountView.as_view(), name='view'),

    path('check_nickname/<str:nickname>/', CheckNicknameAvailable.as_view(), name='check_nickname'),
    path('check_email/<str:email>/', CheckEmailAvailable.as_view(), name='check_email'),

    path('delete/<str:nickname>/', AccountDelete.as_view(), name='delete'),
]