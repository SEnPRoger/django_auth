from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('<str:nickname>/', PostViewSet.as_view({'get': 'get_posts_by_author'}), name='get_posts_by_author'),
]