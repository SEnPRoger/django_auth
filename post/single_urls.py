from post.views import *
from like.views import LikeView
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('<slug:slug>/like', LikeView.as_view(), name='like_post'),
    path('<slug:slug>/', PostRetrieveUpdateDestroy.as_view(), name='view_post'),
    path('add/', PostRetrieveUpdateDestroy.as_view(), name='add_post'),
]