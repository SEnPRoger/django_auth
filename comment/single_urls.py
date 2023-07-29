from comment.views import *
from like.views import LikeView
from django.urls import path, include

app_name = "comment"

urlpatterns = [
    path('<int:comment_id>/like', LikeView.as_view(), name='like_comment'),
    path('<int:comment_replies_id>/replies', CommentListView.as_view(), name='comment_replies'),
    path('<int:id>/', CommentRetrieveUpdateDestroy.as_view(), name='edit_remove_comment'),
    path('add/', CommentRetrieveUpdateDestroy.as_view(), name='add_comment'),
]