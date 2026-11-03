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
from .models import ContentPage, Enquiry, HomePage

class WebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content', verbosity=0)
    def setUp(self):
        cache.clear()
    def test_public_pages_and_languages(self):
        for url in ['/ar/','/en/','/ar/projects/','/en/services/','/ar/projects/anb-golden-belt/','/quote/?lang=ar','/quote/?lang=en']:
            with self.subTest(url=url):
                r=self.client.get(url)
                self.assertEqual(r.status_code,200)
                self.assertNotContains(r,'Welcome to your new Wagtail site')
        self.assertContains(self.client.get('/ar/'),'dir="rtl"')
        self.assertContains(self.client.get('/en/'),'dir="ltr"')
    def test_home_redirect(self):
        self.assertRedirects(self.client.get('/'),'/ar/',fetch_redirect_response=False)
    def test_seed_preserves_editor_changes(self):
        p=HomePage.objects.get(slug='ar');p.headline='Edited';p.save_revision().publish()
        count=Page.objects.count();call_command('seed_content',verbosity=0)
        p.refresh_from_db();self.assertEqual(p.headline,'Edited');self.assertEqual(Page.objects.count(),count)
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
        for url in ['/admin/', f'/admin/pages/{page.pk}/edit/', '/django-admin/home/enquiry/']:
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

class NoSourceImagesTests(TestCase):
    def test_seed_and_home_work_without_private_source_images(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory, override_settings(BASE_DIR=Path(directory)):
            call_command('seed_content',verbosity=0)
            self.assertEqual(self.client.get('/ar/').status_code,200)
            self.assertEqual(self.client.get('/en/').status_code,200)
