# Generated by Django 4.2.2 on 2023-07-16 13:27

from django.db import migrations, models
import post.models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_post_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, default=post.models.generate_slug, null=True),
        ),
    ]