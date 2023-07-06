from django.db.models.signals import pre_save
from django.dispatch import receiver
from account.models import Account, VerifiedAccount

@receiver(pre_save, sender=Account)
def compare_values_on_save(sender, instance, **kwargs):
    # Your custom logic to compare values and perform actions before saving the model
    # You can access the previous and new values using instance.field_name

    # Example: Comparing the 'variable' field
    if instance.pk is not None:
        # If the instance already exists in the database (updating)
        previous_instance = Account.objects.get(pk=instance.pk)
        if instance.is_verify != previous_instance.variable:
            if instance.is_verify == True:
                verify_request = VerifiedAccount.objects.create(account=instance, is_verified=True)
            else:
                verify_request = VerifiedAccount.objects.get(account=instance)
                verify_request.delete()
    else:
        # If the instance is new and being created (not updating)
        pass