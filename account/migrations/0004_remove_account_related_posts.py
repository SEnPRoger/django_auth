# Generated by Django 4.2.2 on 2023-07-20 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_account_related_posts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='related_posts',
        ),
    ]