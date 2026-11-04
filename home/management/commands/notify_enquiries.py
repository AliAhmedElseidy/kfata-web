from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from home.models import Enquiry
from home.mail import notification_route

class Command(BaseCommand):
    help='Retry notification for saved enquiries (may repeat after interrupted delivery).'
    def handle(self, **kwargs):
        route=notification_route()
        if not route:
            raise CommandError('Configure outgoing mail in Wagtail first.')
        for item in Enquiry.objects.filter(notification_sent=False).iterator():
            try:
                sent=send_mail('KFATA: new enquiry',f'Enquiry #{item.pk}: {settings.PUBLIC_BASE_URL}/admin/snippets/home/enquiry/edit/{item.pk}/',route[0],[route[1]])
            except Exception:
                raise CommandError('Notification delivery failed; enquiries remain saved.') from None
            if not sent: raise CommandError('The email backend did not accept delivery; enquiries remain saved.')
            item.notification_sent=True;item.save(update_fields=['notification_sent'])
            self.stdout.write(str(item.pk))
