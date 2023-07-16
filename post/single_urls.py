from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('add/', PostViewSet.as_view({'post': 'add_post'}), name='add_post'),
    path('<slug:post_slug>/', PostViewSet.as_view({'get': 'get_post_by_slug'}), name='get_post_by_slug'),
]