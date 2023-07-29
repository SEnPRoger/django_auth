from comment.views import *
from django.urls import path, include

app_name = "comment"

urlpatterns = [
    path('<slug:post_slug>/<str:sorting_method>/', CommentListView.as_view(), name='comments_list'),
    path('<slug:post_slug>/', CommentListView.as_view(), name='comments_list'),
]