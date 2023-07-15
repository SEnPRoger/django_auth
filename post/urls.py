from post.views import *
from django.urls import path, include

app_name = "post"

urlpatterns = [
    path('add/', AddPost.as_view(), name='add'),
    path('<int:post_id>/', AddPost.as_view(), name='get'),
]