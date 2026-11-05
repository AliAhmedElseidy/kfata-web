"""Source-grounded bilingual enrichment. Preview first; preserve editor revisions."""
import json
from collections import Counter
from html import escape
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Locale
from home.models import ContentPage, HomePage, PresentationUpdate

PACK_PATH = Path(__file__).resolve().parents[2] / 'content' / 'company_profile.json'

def load_pack():
    pack = json.loads(PACK_PATH.read_text(encoding='utf-8'))
    seen = set()
    for item in pack['pages']:
        identity = (item['parent_slug'], item['slug'])
        if identity in seen:
            raise CommandError(f'Duplicate source page: {identity}')
        seen.add(identity)
        if item['kind'] not in {'page','service','sector','project'}:
            raise CommandError('Unsupported content kind.')
        if not any(item['source'].values()):
            raise CommandError(f'Missing source pages: {item["slug"]}')
        for lang in ['ar','en']:
            copy = item['languages'][lang]
            if not copy['title'] or not copy['summary'] or not copy['paragraphs']:
                raise CommandError(f'Incomplete {lang} copy: {item["slug"]}')
    return pack

def source_html(copy):
    paragraphs = ''.join('<p>' + escape(p) + '</p>' for p in copy['paragraphs'])
    if copy['details']:
        paragraphs += '<ul>' + ''.join('<li>' + escape(p) + '</li>' for p in copy['details']) + '</ul>'
    return paragraphs

class Command(BaseCommand):
    help = 'Preview or apply sourced bilingual content; publication requires --apply --publish.'
    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Save new revisions. Default is read-only preview.')
        parser.add_argument('--publish', action='store_true', help='Publish eligible source-backed copy; requires --apply.')
    def handle(self, **options):
        if options['publish'] and not options['apply']:
            raise CommandError('--publish requires --apply.')
        pack = load_pack()
        totals = Counter()
        # Translation keys come from the first language, including preview plans.
        with transaction.atomic():
            for item in pack['pages']:
                pair = []
                for language in ['ar','en']:
                    result, page = self.process(item, language, pair, pack['version'], options)
                    totals[result] += 1
                    self.stdout.write(f'{language} {item["slug"]}: {result}')
                    pair.append(page)
        label = 'APPLIED' if options['apply'] else 'PREVIEW ONLY — no changes'
        self.stdout.write(self.style.SUCCESS(label + ': ' + ', '.join(f'{key}={value}' for key,value in sorted(totals.items()))))
        return None
    def process(self, item, language, pair, version, options):
        locale = Locale.objects.filter(language_code=language).first()
        if not locale:
            return 'missing locale', None
        root = HomePage.objects.filter(locale=locale).first()
        if not root:
            return 'missing language home', None
        if item['parent_slug']:
            parents = ContentPage.objects.child_of(root).filter(slug=item['parent_slug'])
            if options['apply']:
                parents = parents.select_for_update()
            parent = parents.first()
        else:
            parent = root
        if not parent:
            return 'missing parent', None
        marker = f'source-enrichment-v1:{item["slug"]}:{language}'
        applied = PresentationUpdate.objects.filter(key=marker).select_related('page').first()
        if applied:
            return 'already applied', applied.page.specific
        query = ContentPage.objects.child_of(parent).filter(slug=item['slug'])
        if options['apply']:
            query = query.select_for_update()
        page = query.first()
        if page:
            if page.kind != item['kind']:
                return 'kind conflict', page
            latest = page.get_latest_revision()
            if latest and latest.user_id:
                return 'editor revision preserved', page
            if page.live and page.has_unpublished_changes:
                return 'pending draft preserved', page
            # Avoid publishing text inserted into a deliberately restricted page.
            if options['publish'] and page.get_view_restrictions().exists():
                return 'restricted page preserved', page
        if not options['apply']:
            return ('would update' if page else 'would create'), page
        copy = item['languages'][language]
        created = page is None
        if created:
            page = ContentPage(title=copy['title'], slug=item['slug'], kind=item['kind'], locale=locale, live=False)
            if pair and pair[0]:
                page.translation_key = pair[0].translation_key
            parent.add_child(instance=page)
        # Preserve curated image/video/gallery and layout blocks. Refresh the first
        # source-generated heading, or append a section when none exists.
        source_section = {'visible':True, 'tone':'stone', 'eyebrow':'KFATA', 'title':copy['title'], 'text':source_html(copy)}
        body = []
        replaced = False
        for block in page.body:
            if block.block_type == 'heading' and not replaced:
                old = dict(block.value)
                old.update(title=source_section['title'], text=source_section['text'])
                body.append(('heading', old))
                replaced = True
            else:
                body.append((block.block_type, block.value))
        if not replaced:
            body.append(('heading', source_section))
        page.body = body
        page.summary = copy['summary']
        page.search_description = copy['summary'][:160]
        if item['slug'] == 'warehouse-finishing' and page.title in {'تشطيبات مستودع صناعي','Industrial warehouse finishing'}:
            page.title = copy['title']
        if page.kind == 'project':
            if not page.scope:
                page.scope = copy['summary'][:250]
            if not page.location and item['location']:
                locations = {'Riyadh':'الرياض','Jeddah':'جدة','Abha':'أبها','Al Majmaah':'المجمعة','Al Muzahmiyah':'المزاحمية','Al Ghat':'الغاط','Rumah':'رماح','Southern region':'المنطقة الجنوبية','Eastern region':'المنطقة الشرقية'}
                page.location = locations.get(item['location'], item['location']) if language == 'ar' else item['location']
        if item['sector_slug']:
            sector = ContentPage.objects.filter(locale=locale, kind='sector', slug=item['sector_slug']).first()
            if sector:
                page.related_sectors.add(sector)
                if not page.sector:
                    page.sector = sector.title
        for slug in item.get('service_slugs', []):
            service = ContentPage.objects.filter(locale=locale, kind='service', slug=slug).first()
            if service:
                page.related_services.add(service)
        # Do not replace contact settings, existing project facts, photographs,
        # permissions, SMTP, statistics, homepages or customer records.
        revision = page.save_revision()
        if options['publish']:
            revision.publish()
        PresentationUpdate.objects.create(page=page, key=marker)
        return ('created' if created else 'updated') + (' and published' if options['publish'] else ' as draft'), page
