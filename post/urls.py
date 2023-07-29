from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('<int:id>/', PostListView.as_view(), name='post_list'),
]