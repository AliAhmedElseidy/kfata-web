from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Enquiry


@receiver(pre_delete, sender=Enquiry)
def delete_private_attachment(sender, instance, **kwargs):
    if instance.attachment and not sender.objects.exclude(pk=instance.pk).filter(attachment=instance.attachment.name).exists():
        # Fail the record deletion if private-file deletion fails, so an operator can retry.
        instance.attachment.storage.delete(instance.attachment.name)
