from account.views import *
from django.urls import path, include

app_name = "account"

urlpatterns = [
    path('register/', AccountRegister.as_view(), name='register'),
    path('login/', AccountLogin.as_view(), name='login'),

    # path('<str:nickname>/', AccountView.as_view(), name='view'),
]