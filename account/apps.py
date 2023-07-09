from django.apps import AppConfig

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    # def ready(self):
    #     from account.signals import compare_values_on_save
    #     compare_values_on_save(sender=None, instance=None, created=None)