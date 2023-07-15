from django.db import models

def upload_photo_path(instance, filename):
        extension = filename.split('.')[1]
        return 'photos/{0}/{1}.{2}'.format(instance.author.id, instance.id, extension)

# Create your models here.
class Photo(models.Model):
    file = models.ImageField(upload_to=upload_photo_path, blank=False, null=False)
    author = models.ForeignKey('account.Account', verbose_name='Автор фотографії', blank=False, null=False,
                                on_delete=models.CASCADE)
    upload_date = models.DateTimeField(verbose_name='Дата завантаження', blank=False, null=False, auto_now_add=True)

    def __str__(self):
        return self.author.nickname
    
    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="460" height="259" style="border-radius: 20px"; />' % (self.file.url))
    image_tag.short_description = '🖼 Photo'
    image_tag.allow_tags = True
    
    def save(self, *args, **kwargs):
        if self.author is None:
            image_author = self.author
            self.author = None
            super(Photo, self).save(*args, **kwargs)
            self.author = image_author
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(Photo, self).save(*args, **kwargs)