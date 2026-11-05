"""Install the owner's approved original scene once; never reset panel edits."""
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection
from home.models import BrandSettings, HomePage, PresentationUpdate
from home.scene import validate_scene_settings


class Command(BaseCommand):
    help = 'Preview/install approved scene assets once. --apply --enable explicitly activates both home languages.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--enable', action='store_true')

    @transaction.atomic
    def handle(self, **options):
        if options['enable'] and not options['apply']:
            raise CommandError('--enable requires --apply.')
        brand = BrandSettings.load()
        brand = BrandSettings.objects.select_for_update().get(pk=brand.pk)
        marker = 'construction-scene-v1'
        if PresentationUpdate.objects.filter(key=marker).exists():
            self.stdout.write('Already installed; current panel configuration preserved.')
            return
        fields = ['scene_video', 'scene_video_mobile', 'scene_poster', 'scene_poster_mobile']
        if brand.scene_enabled or any(getattr(brand, field + '_id') for field in fields):
            self.stdout.write('Existing scene configuration preserved; manage it in Brand settings.')
            return
        names = ['desktop.mp4', 'mobile.mp4', 'poster.jpg', 'poster-mobile.jpg']
        root = Path(settings.BASE_DIR) / 'assets' / 'construction-scene'
        if not options['apply']:
            self.stdout.write('PREVIEW ONLY: import ' + ', '.join(names) + (' and enable both home languages.' if options['enable'] else '; activation remains off.'))
            return
        if not all((root / name).is_file() for name in names):
            raise CommandError('Missing approved scene asset in assets/construction-scene/.')
        page = HomePage.objects.filter(locale__language_code='ar').first()
        if not page:
            raise CommandError('Existing Arabic homepage required; do not seed/reset production.')
        collection = Collection.get_first_root_node()
        if collection.get_view_restrictions().exclude(restriction_type='none').exists():
            raise CommandError('The default asset collection is restricted; select a public collection deliberately.')
        for field, name in zip(fields, names):
            model = get_document_model() if name.endswith('.mp4') else get_image_model()
            with (root / name).open('rb') as file:
                asset = model.objects.create(title='KFATA original construction concept — ' + name, collection=collection, file=File(file, name='kfata-construction-' + name))
            if name.endswith('.mp4'):
                asset.get_file_size();asset.get_file_hash()
            setattr(brand, field, asset)
        brand.scene_enabled = options['enable']
        validate_scene_settings(brand)
        brand.save(update_fields=fields + ['scene_enabled'])
        PresentationUpdate.objects.create(page=page, key=marker)
        self.stdout.write('Approved assets installed. Scene enabled for both home languages.' if brand.scene_enabled else 'Approved assets installed; activation remains off.')
