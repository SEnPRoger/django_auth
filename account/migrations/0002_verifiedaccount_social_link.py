# Generated by Django 4.2.2 on 2023-07-14 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifiedaccount',
            name='social_link',
            field=models.TextField(blank=True, null=True),
        ),
    ]