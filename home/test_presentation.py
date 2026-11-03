from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from wagtail.models import Page,PageViewRestriction
from home.models import HomePage,ContentPage,BrandSettings,PresentationUpdate,SMTPSettings
from urllib.parse import urlsplit
from xml.etree import ElementTree

class PresentationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content',verbosity=0)
        call_command('import_profile_drafts',verbosity=0)
    def update(self):call_command('refresh_presentation',apply=True,stdout=StringIO())
    def test_preview_is_read_only(self):
        before=list(HomePage.objects.values_list('headline','latest_revision_id'))
        count=Page.objects.count()
        call_command('refresh_presentation',stdout=StringIO())
        self.assertEqual(list(HomePage.objects.values_list('headline','latest_revision_id')),before)
        self.assertEqual(Page.objects.count(),count)
        self.assertFalse(PresentationUpdate.objects.exists())
    def test_update_preserves_owner_revisions_pending_drafts_and_mail(self):
        owner=get_user_model().objects.create_superuser('presentation-owner','owner@example.test','test-only')
        home=HomePage.objects.get(slug='ar');home.headline='Owner headline';home.save_revision(user=owner).publish()
        service=ContentPage.objects.get(slug='renovation',locale__language_code='en')
        service.summary='Pending owner draft';revision=service.save_revision(user=owner)
        mail=SMTPSettings.load();mail.host='smtp.example.test';mail.password_ciphertext='preserve-test-ciphertext';mail.save()
        self.update()
        home.refresh_from_db();service.refresh_from_db();mail.refresh_from_db()
        self.assertEqual(home.headline,'Owner headline')
        self.assertEqual(service.latest_revision_id,revision.pk)
        self.assertTrue(service.has_unpublished_changes)
        self.assertEqual(mail.host,'smtp.example.test');self.assertEqual(mail.password_ciphertext,'preserve-test-ciphertext')
        p=HomePage.objects.get(slug='en');p.body=[];p.save_revision().publish()
        brand=BrandSettings.load();brand.footer_columns=[];brand.footer_intro_ar='';brand.save()
        policy=ContentPage.objects.get(slug='terms',locale__language_code='en')
        policy.slug='website-terms';policy.save_revision().publish()
        count=Page.objects.count()
        self.update();p.refresh_from_db();self.assertFalse(p.body)
        self.assertEqual(Page.objects.count(),count)
        self.assertFalse(BrandSettings.load().footer_columns)
        self.assertEqual(BrandSettings.load().footer_intro_ar,'')
    def test_curated_pages_footer_policies_and_galleries_are_public_and_translated(self):
        self.update()
        for lang in ['ar','en']:
            response=self.client.get('/'+lang+'/');self.assertEqual(response.status_code,200)
            self.assertContains(response,'tone-stone');self.assertContains(response,'process-steps')
            self.assertContains(response,'https://wa.me/966504552257')
            for slug in ['terms','cookies','quality-safety']:
                self.assertContains(response,f'href="/{lang}/{slug}/"')
                self.assertEqual(self.client.get(f'/{lang}/{slug}/').status_code,200)
            project=self.client.get(f'/{lang}/projects/anb-new-tower/')
            self.assertContains(project,'data-gallery-image',count=3)
            self.assertContains(project,f'href="/{lang}/services/renovation/"')
        # A chooser can retain drafts/private pages without exposing them publicly.
        p=ContentPage.objects.get(slug='design-build',locale__language_code='en');p.unpublish()
        private=ContentPage.objects.get(slug='furnishing',locale__language_code='en')
        PageViewRestriction.objects.create(page=private,restriction_type='password',password='test-only')
        response=self.client.get('/en/')
        self.assertNotContains(response,'href="/en/services/design-build/"')
        self.assertNotContains(response,'href="/en/services/furnishing/"')
        self.assertNotContains(response,'anb-golden-belt')
        self.assertEqual(self.client.get('/en/projects/anb-golden-belt/').status_code,404)
        self.assertIn('AI-generated illustration',response.content.decode())
        sitemap=ElementTree.fromstring(self.client.get('/sitemap.xml').content)
        paths=[urlsplit(n.text).path for n in sitemap.iter() if n.tag.endswith('}loc')]
        self.assertNotIn('/',paths)
        self.assertIn('/en/terms/',paths)
