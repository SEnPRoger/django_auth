from django.db import models
from account.models import Account
from post.models import Post
from comment.models import Comment

# Create your models here.
class Like(models.Model):
    account     = models.ForeignKey('account.Account', blank=False, on_delete=models.CASCADE)
    date        = models.DateTimeField(auto_now_add=True)
    post        = models.ForeignKey('post.Post', blank=True, null=True, related_name='post_likes', on_delete=models.CASCADE)
    comment     = models.ForeignKey('comment.Comment', blank=True, null=True, related_name='comment_likes', on_delete=models.CASCADE)