from django.apps import AppConfig
from django.db import connection

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    # def ready(self):
    #     with connection.cursor() as cursor:
    #         cursor.execute("CREATE TABLE my_cache_table (cache_key VARCHAR(255) PRIMARY KEY, cache_value BYTEA, cache_timeout TIMESTAMP)")

    # def ready(self):
    #     from account.signals import compare_values_on_save
    #     compare_values_on_save(sender=None, instance=None, created=None)