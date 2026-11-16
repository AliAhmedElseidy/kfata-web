from django.contrib.auth.signals import user_login_failed
from django_otp.forms import otp_verification_failed
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Enquiry
from .security import ADMIN_PREFIXES, logger


@receiver(pre_delete, sender=Enquiry)
def delete_private_attachment(sender, instance, **kwargs):
    if instance.attachment and not sender.objects.exclude(pk=instance.pk).filter(attachment=instance.attachment.name).exists():
        # Fail the record deletion if private-file deletion fails, so an operator can retry.
        instance.attachment.storage.delete(instance.attachment.name)

@receiver(user_login_failed)
def report_failed_login(sender, request, **kwargs):
    if request is not None and request.path.startswith(ADMIN_PREFIXES):
        logger.warning("event=admin_password_failure")


@receiver(otp_verification_failed)
def report_failed_otp(sender, **kwargs):
    logger.warning("event=admin_otp_failure")
