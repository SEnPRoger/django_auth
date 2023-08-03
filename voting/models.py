from django.db import models

# Create your models here.
class Poll(models.Model):
    title           = models.TextField(blank=False)
    author          = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    published_date  = models.DateTimeField(auto_now_add=True)
    is_edited       = models.BooleanField(default=False)

class Choice(models.Model):
    poll            = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    content         = models.CharField(max_length=264, blank=False)

class Vote(models.Model):
    choice          = models.ForeignKey(Choice, related_name='votes', on_delete=models.CASCADE)
    voted_by        = models.ForeignKey('account.Account', on_delete=models.CASCADE)