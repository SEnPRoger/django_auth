from django.db import models

# Create your models here.
class Post(models.Model):
    content         = models.CharField(verbose_name='Вміст посту', blank=False, max_length=600)
    author          = models.ForeignKey('account.Account', verbose_name='Автор публікації',
                                         related_name='author_set', on_delete=models.DO_NOTHING)
    photos = models.ManyToManyField('photo.Photo', verbose_name='Фотографії', blank=True)
    published_date  = models.DateTimeField(verbose_name='Дата публікації', auto_now_add=True)
    is_edited = models.BooleanField(verbose_name='Пост було редаговано', default=False)

    reply           = models.ForeignKey('self', verbose_name='Відповідь на пост', related_name='reply_set',
                                         blank=True, null=True, on_delete=models.SET_NULL)
    is_reply        = models.BooleanField(verbose_name='Чи це є репост', default=False)
    device          = models.CharField(max_length=8, blank=False, null=False) # 'pc' or 'mobile'