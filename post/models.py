from django.db import models
from datetime import datetime
import random

def generate_slug():
        alfa = "abcdefghijklmnopqrstuvwxyz"
        digit_pairs = []
        output_slug = ""
        
        number = int(str(datetime.now().timestamp()).replace('.', ''))
        number_str = str(number)

        for i in range(0, len(number_str) - 1, 2):
            pair = int(number_str[i:i + 2]) % 26  # Ensure pair is within the range of the alphabet string
            digit_pairs.append(pair)

        for pair in digit_pairs:
            output_slug += alfa[pair]

        out_list = list(output_slug)
        random.shuffle(out_list)
        output_slug = ''.join(out_list)

        repeating_indices = [i for i, char in enumerate(output_slug) if output_slug.count(char) > 1]

        for index in repeating_indices:
            char = output_slug[index]
            if index % 2 == 0:
                output_slug = output_slug[:index] + char.lower() + output_slug[index + 1:]
            else:
                output_slug = output_slug[:index] + char.upper() + output_slug[index + 1:]

        return output_slug

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
    slug            = models.SlugField(blank=True, null=True, default=generate_slug)