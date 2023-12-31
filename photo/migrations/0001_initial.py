# Generated by Django 4.2.2 on 2023-07-15 00:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import photo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to=photo.models.upload_photo_path)),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата завантаження')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор фотографії')),
            ],
        ),
    ]
