from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from home.models import Enquiry


class Command(BaseCommand):
    help = 'Delete enquiries and private attachments past the approved retention period. Dry run unless --apply.'

    def add_arguments(self, parser):
        parser.add_argument('--apply',action='store_true')

    def handle(self, **options):
        cutoff=timezone.now()-timedelta(days=settings.ENQUIRY_RETENTION_DAYS)
        candidates=Enquiry.objects.filter(created_at__lt=cutoff)
        if not options['apply']:
            self.stdout.write(f'Eligible enquiries: {candidates.count()}; no data deleted.')
            return
        deleted=0
        for pk in candidates.values_list('pk',flat=True).iterator():
            with transaction.atomic():
                item=Enquiry.objects.select_for_update().filter(pk=pk,created_at__lt=cutoff).first()
                if not item: continue
                try: item.delete()
                except Exception as error:
                    raise CommandError('Retention deletion failed; record kept for retry.') from error
                deleted+=1
        self.stdout.write(self.style.SUCCESS(f'Retention applied; deleted enquiries: {deleted}.'))
