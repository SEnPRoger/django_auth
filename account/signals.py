from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from account.models import Account
from datetime import datetime, timedelta
from django.utils import timezone

@receiver(pre_save, sender=Account)
def compare_values_on_save(sender, instance, created, **kwargs):
    if not created:
        # If the instance is not newly created (updating)
        previous_instance = Account.objects.get(pk=instance.pk)

        if instance.nickname != previous_instance.nickname:
            current_datetime = timezone.now()
            time_diff = current_datetime - previous_instance.changed_nickname

            if time_diff < timedelta(days=7):
                instance.nickname = previous_instance.nickname
            else:
                instance.changed_nickname = timezone.now()