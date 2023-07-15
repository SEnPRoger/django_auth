from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('add/', PostViewSet.as_view({'post': 'add_post'}), name='add_post'),
    path('<int:post_id>/', PostViewSet.as_view({'get': 'get_post_by_id'}), name='get_post_by_id'),
    path('<str:nickname>/', PostViewSet.as_view({'get': 'get_posts_by_author'}), name='get_posts_by_author'),
]