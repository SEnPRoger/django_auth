from django.db import models

# Create your models here.
class Comment(models.Model):
    post            = models.ForeignKey('post.Post', blank=False, on_delete=models.CASCADE, related_name='comments')
    content         = models.CharField(verbose_name='Вміст коментарю', blank=False, max_length=600)
    author          = models.ForeignKey('account.Account', related_name='author_comment_set', on_delete=models.DO_NOTHING)
    photos          = models.ManyToManyField('photo.Photo', verbose_name='Фотографії', blank=True)
    published_date  = models.DateTimeField(verbose_name='Дата публікації', auto_now_add=True)
    is_edited       = models.BooleanField(verbose_name='Коментар було редаговано', default=False)
    reply           = models.ForeignKey('self', related_name='reply_comment_set', blank=True, null=True, on_delete=models.SET_NULL)
    device          = models.CharField(max_length=8, blank=False, null=False)