import io
import tempfile
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image
from wagtail.models import Page
from .forms import EnquiryForm
from .models import BrandSettings, ContentPage, Enquiry, HomePage

class WebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content', verbosity=0)
        brand = BrandSettings.load()
        brand.enquiries_enabled=True;brand.email='contact@example.test';brand.phone='123456789';brand.save()
        for p in ContentPage.objects.filter(slug='privacy'):
            p.save_revision().publish()
    def setUp(self):
        cache.clear()
    def test_public_pages_and_languages(self):
        for url in ['/ar/','/en/','/ar/projects/','/en/services/','/ar/projects/residential-villas/','/quote/?lang=ar','/quote/?lang=en']:
            with self.subTest(url=url):
                r=self.client.get(url)
                self.assertEqual(r.status_code,200)
                self.assertNotContains(r,'Welcome to your new Wagtail site')
        self.assertContains(self.client.get('/ar/'),'dir="rtl"')
        self.assertContains(self.client.get('/en/'),'dir="ltr"')
    def test_home_redirect(self):
        self.assertRedirects(self.client.get('/'),'/ar/',fetch_redirect_response=False)
    def test_generated_links_match_routable_tree(self):
        for page in ContentPage.objects.live().public():
            self.assertEqual(self.client.get(page.url).status_code,200,page.url)
        self.assertNotContains(self.client.get('/ar/'),'href="/home/')
    def test_seed_preserves_editor_changes(self):
        p=HomePage.objects.get(slug='ar');p.headline='Edited';p.save_revision().publish()
        count=Page.objects.count();call_command('seed_content',verbosity=0)
        p.refresh_from_db();self.assertEqual(p.headline,'Edited');self.assertEqual(Page.objects.count(),count)
        p.body=[];p.save_revision().publish();call_command('seed_content',verbosity=0)
        p.refresh_from_db();self.assertFalse(p.body)
        from wagtail.images import get_image_model
        image=get_image_model().objects.first();image.title='Editor alternative text';image.save()
        total=get_image_model().objects.count();call_command('seed_content',verbosity=0)
        self.assertEqual(get_image_model().objects.count(),total)
    def test_drafts_and_sitemap(self):
        self.assertEqual(self.client.get('/ar/certifications/').status_code,404)
        r=self.client.get('/sitemap.xml');self.assertEqual(r.status_code,200)
        self.assertNotContains(r,'/certifications/')
    @override_settings(SITE_INDEXABLE=False)
    def test_preview_not_indexable(self):
        self.assertEqual(self.client.get('/ar/')['X-Robots-Tag'],'noindex, nofollow')
        self.assertContains(self.client.get('/robots.txt'),'Disallow: /')
    @override_settings(SITE_INDEXABLE=True)
    def test_production_metadata(self):
        r=self.client.get('/ar/')
        self.assertContains(r,'rel="canonical"')
        self.assertContains(r,'hreflang="en"')
        self.assertNotContains(r,'name="robots" content="noindex')
    def valid_data(self):
        return {'name':'Test client','email':'client@example.test','phone':'123456789','message':'Test project enquiry','consent':'on'}
    @override_settings(EMAIL_HOST='smtp.example.test',ENQUIRY_EMAIL='inbox@example.test')
    @patch('home.views.send_mail',side_effect=OSError('SMTP offline'))
    def test_smtp_failure_keeps_enquiry(self,_):
        r=self.client.post('/quote/',self.valid_data())
        self.assertEqual(r.status_code,302)
        self.assertEqual(Enquiry.objects.count(),1)
        self.assertFalse(Enquiry.objects.first().notification_sent)
    def test_spam_and_invalid_files_rejected(self):
        data=self.valid_data();data['website']='spam';self.client.post('/quote/',data)
        self.assertFalse(Enquiry.objects.exists())
        data=self.valid_data();data['attachment']=SimpleUploadedFile('photo.jpg',b'<script>alert(1)</script>',content_type='image/jpeg')
        r=self.client.post('/quote/',data)
        self.assertEqual(r.status_code,200);self.assertFalse(Enquiry.objects.exists())
    def test_image_reencoded(self):
        out=io.BytesIO();Image.new('RGB',(8,8),'red').save(out,'PNG')
        form=EnquiryForm(self.valid_data(),{'attachment':SimpleUploadedFile('image.png',out.getvalue()+b'APPENDED PAYLOAD')})
        self.assertTrue(form.is_valid(),form.errors)
        f=form.cleaned_data['attachment'];self.assertEqual(f.name,'attachment.jpg');self.assertNotIn(b'APPENDED PAYLOAD',f.read())
    def test_rate_limit(self):
        for _ in range(5): self.client.post('/quote/',{})
        self.assertEqual(self.client.post('/quote/',self.valid_data()).status_code,429)
        self.assertFalse(Enquiry.objects.exists())
    def test_attachment_requires_model_permission(self):
        item=Enquiry.objects.create(name='Private',email='a@example.test',phone='1',message='x')
        self.assertEqual(self.client.get(f'/private/enquiry/{item.pk}/').status_code,302)
        user=get_user_model().objects.create_user('staff',password='test-only-password',is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get(f'/private/enquiry/{item.pk}/').status_code,403)
        user.user_permissions.add(Permission.objects.get(codename='view_enquiry'))
        self.assertEqual(self.client.get(f'/private/enquiry/{item.pk}/').status_code,404)
    def test_csrf_required(self):
        from django.test import Client
        self.assertEqual(Client(enforce_csrf_checks=True).post('/quote/',self.valid_data()).status_code,403)
    def test_unknown_page(self):
        self.assertEqual(self.client.get('/no-such-page/').status_code,404)
    def test_admin_editors_render(self):
        user=get_user_model().objects.create_superuser('owner','owner@example.test','test-only-password')
        self.client.force_login(user)
        page=HomePage.objects.get(slug='ar')
        for url in ['/admin/', f'/admin/pages/{page.pk}/edit/', '/django-admin/home/enquiry/', '/admin/snippets/home/enquiry/']:
            with self.subTest(url=url): self.assertEqual(self.client.get(url).status_code,200)
    def test_private_file_download_and_public_denial(self):
        from django.core.files.storage import FileSystemStorage
        storage=Enquiry._meta.get_field('attachment').storage
        with tempfile.TemporaryDirectory() as directory:
            Enquiry._meta.get_field('attachment').storage=FileSystemStorage(location=directory)
            try:
                item=Enquiry.objects.create(name='Private',email='a@example.test',phone='1',message='x',attachment=SimpleUploadedFile('proof.jpg',b'private-test-content'))
                user=get_user_model().objects.create_user('reviewer',password='test-only-password',is_staff=True)
                user.user_permissions.add(Permission.objects.get(codename='view_enquiry'))
                self.client.force_login(user)
                response=self.client.get(f'/private/enquiry/{item.pk}/')
                self.assertEqual(response.status_code,200)
                self.assertEqual(b''.join(response.streaming_content),b'private-test-content')
                self.assertEqual(response['Cache-Control'],'private, no-store')
                self.assertEqual(self.client.get('/media/'+item.attachment.name).status_code,404)
            finally:
                Enquiry._meta.get_field('attachment').storage=storage

    def test_enquiry_gate_rejects_unreviewed_launch(self):
        brand=BrandSettings.load();brand.enquiries_enabled=False;brand.save()
        self.assertNotContains(self.client.get('/quote/'),'<form')
        self.assertEqual(self.client.post('/quote/',self.valid_data()).status_code,503)
        self.assertFalse(Enquiry.objects.exists())
        self.assertContains(self.client.get('/quote/?lang=en'),'href="/en/projects/"')

    def test_editor_draft_and_publisher_permissions(self):
        from django.contrib.auth.models import Group

        call_command('setup_roles')
        editor=get_user_model().objects.create_user('editor',password='test-only-password')
        editor.groups.add(Group.objects.get(name='KFATA Editors'))
        publisher=get_user_model().objects.create_user('publisher',password='test-only-password')
        publisher.groups.add(Group.objects.get(name='KFATA Publishers'))
        page=HomePage.objects.get(slug='ar')
        self.assertTrue(page.permissions_for_user(editor).can_edit())
        self.assertFalse(page.permissions_for_user(editor).can_publish())
        self.assertTrue(page.permissions_for_user(publisher).can_publish())
        self.assertFalse(editor.has_perm('home.view_enquiry'))
        previous=page.headline;page.headline='Draft headline';page.save_revision()
        self.assertContains(self.client.get('/ar/'),previous.split('\n')[0])
        self.assertNotContains(self.client.get('/ar/'),'Draft headline')

    def test_wagtail_enquiry_edit_and_permission(self):
        item=Enquiry.objects.create(name='Private',email='a@example.test',phone='1',message='x')
        user=get_user_model().objects.create_superuser('manager','owner@example.test','test-only-password')
        self.client.force_login(user)
        self.assertContains(self.client.get(f'/admin/snippets/home/enquiry/edit/{item.pk}/'),'Private')
        self.assertEqual(self.client.get('/admin/snippets/home/enquiry/add/').status_code,302)
        self.assertEqual(Enquiry.objects.count(),1)

    def test_related_projects_and_structured_data(self):
        parent=ContentPage.objects.get(slug='projects',locale__language_code='en')
        peer=ContentPage(title='Related test project',slug='related-test',locale=parent.locale,kind='project',sector='Banking')
        parent.add_child(instance=peer);peer.save_revision().publish()
        r=self.client.get('/en/projects/anb-new-tower/')
        self.assertContains(r,'Related projects')
        self.assertContains(r,'BreadcrumbList')
        self.assertContains(r,'Related test project')
        self.assertNotContains(r,'ANB — Al Hizam Al Thahabi')
        r=self.client.get('/en/projects/')
        self.assertEqual(len(r.context['sectors']),len(set(r.context['sectors'])))

    def test_source_import_preserves_edits_and_keeps_extra_projects_draft(self):
        call_command('import_profile_drafts',verbosity=0)
        total=Page.objects.count()
        self.assertEqual(ContentPage.objects.filter(slug='school-muzahmiyah').count(),2)
        self.assertFalse(ContentPage.objects.filter(slug='school-muzahmiyah',live=True).exists())
        self.assertEqual(self.client.get('/ar/projects/anb-golden-belt/').status_code,404)
        brand=BrandSettings.load();logo=brand.logo_id;self.assertIsNotNone(logo)
        page=ContentPage.objects.get(slug='about',locale__language_code='ar')
        page.body=[('heading',{'title':'Owner content','eyebrow':'','text':'<p>Keep this copy.</p>'})]
        page.save_revision().publish()
        call_command('import_profile_drafts',verbosity=0)
        self.assertEqual(Page.objects.count(),total)
        self.assertContains(self.client.get('/ar/about/'),'Owner content')
        self.assertEqual(BrandSettings.load().logo_id,logo)

    def test_retention_deletes_expired_records_and_private_files_only_on_apply(self):
        from datetime import timedelta
        from django.utils import timezone
        from django.core.files.storage import FileSystemStorage
        field=Enquiry._meta.get_field('attachment');original=field.storage
        with tempfile.TemporaryDirectory() as directory:
            field.storage=FileSystemStorage(location=directory)
            try:
                old=Enquiry.objects.create(name='Retention test',email='test@example.test',phone='1',message='Synthetic',attachment=SimpleUploadedFile('proof.jpg',b'test-only'))
                Enquiry.objects.filter(pk=old.pk).update(created_at=timezone.now()-timedelta(days=91))
                recent=Enquiry.objects.create(name='Recent test',email='test@example.test',phone='1',message='Synthetic')
                name=old.attachment.name
                call_command('purge_enquiries',verbosity=0)
                self.assertTrue(field.storage.exists(name));self.assertTrue(Enquiry.objects.filter(pk=old.pk).exists())
                call_command('purge_enquiries',apply=True,verbosity=0)
                self.assertFalse(field.storage.exists(name));self.assertFalse(Enquiry.objects.filter(pk=old.pk).exists())
                self.assertTrue(Enquiry.objects.filter(pk=recent.pk).exists())
            finally: field.storage=original

    def test_approved_launch_has_bilingual_privacy_and_records_consent_version(self):
        call_command('configure_reviewed_launch',hosting_country='Saudi Arabia',enable_enquiries=True,verbosity=0)
        for lang in ['ar','en']:
            self.assertContains(self.client.get(f'/{lang}/privacy/'),'90')
            self.assertContains(self.client.get('/quote/?lang='+lang),f'/{lang}/privacy/')
        brand=BrandSettings.load();brand.privacy_version='test-version';brand.save()
        self.client.post('/quote/',self.valid_data())
        self.assertEqual(Enquiry.objects.get().privacy_version,'test-version')

class NoSourceImagesTests(TestCase):
    def test_seed_and_home_work_without_private_source_images(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory, override_settings(BASE_DIR=Path(directory)):
            call_command('seed_content',verbosity=0)
            self.assertEqual(self.client.get('/ar/').status_code,200)
            self.assertEqual(self.client.get('/en/').status_code,200)
