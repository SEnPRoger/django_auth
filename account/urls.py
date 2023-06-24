from account.views import *
from django.urls import path, include

app_name = "account"

urlpatterns = [
    path('register/', AccountRegister.as_view(), name='register'),
    path('login/', AccountLogin.as_view(), name='login'),

    path('private/', AccountPrivateView.as_view(), name='private_view'),
    path('<str:nickname>/', AccountView.as_view(), name='view'),

    path('check_nickname/<str:nickname>/', CheckNicknameAvailable.as_view(), name='check_nickname'),
    path('check_email/<str:email>/', CheckEmailAvailable.as_view(), name='check_email'),
]