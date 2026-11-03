from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from home.models import Enquiry

class Command(BaseCommand):
    help='Retry notification for saved enquiries (may repeat after interrupted delivery).'
    def handle(self, **kwargs):
        if not settings.EMAIL_HOST or not settings.ENQUIRY_EMAIL:
            raise CommandError('SMTP and ENQUIRY_EMAIL must be configured first.')
        for item in Enquiry.objects.filter(notification_sent=False).iterator():
            send_mail('KFATA: new enquiry',f'Enquiry #{item.pk} is available in the admin.',settings.DEFAULT_FROM_EMAIL,[settings.ENQUIRY_EMAIL])
            item.notification_sent=True;item.save(update_fields=['notification_sent'])
            self.stdout.write(str(item.pk))
