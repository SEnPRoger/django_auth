# Generated by Django 4.2.2 on 2023-07-22 00:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_account_related_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='blocked_accounts',
            field=models.ManyToManyField(blank=True, related_name='blocked_accounts_set', to=settings.AUTH_USER_MODEL, verbose_name='Blocked accounts'),
        ),
        migrations.AlterField(
            model_name='account',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscribers_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
