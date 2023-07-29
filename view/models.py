from django.db import models

# Create your models here.
class View(models.Model):
    post        = models.ForeignKey('post.Post', related_name='views', on_delete=models.CASCADE)
    account     = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    viewed_date = models.DateTimeField(auto_now_add=True)
    device      = models.CharField(max_length=8)