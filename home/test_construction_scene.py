import io
import tempfile
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, CollectionViewRestriction
from home.models import BrandSettings, HomePage, ContentPage


class ConstructionSceneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content', stdout=io.StringIO())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        override = override_settings(MEDIA_ROOT=self.temp.name)
        override.enable();self.addCleanup(override.disable)
        self.bytes = b'\x00\x00\x00\x18ftypisom' + bytes(range(80))
        self.doc = get_document_model().objects.create(title='Approved scene', file=SimpleUploadedFile('scene.mp4', self.bytes))
        picture = io.BytesIO();Image.new('RGB', (64,36), 'gray').save(picture, format='JPEG')
        self.poster = get_image_model().objects.create(title='Completed concept', file=SimpleUploadedFile('completed.jpg',picture.getvalue(),content_type='image/jpeg'))
        self.brand = BrandSettings.load();self.brand.scene_enabled=True;self.brand.scene_video=self.doc;self.brand.scene_poster=self.poster;self.brand.save()

    def test_both_home_languages_use_editable_scene_with_immediate_actions(self):
        for lang in ['ar','en']:
            response = self.client.get('/'+lang+'/')
            self.assertContains(response,'data-construction-scene')
            self.assertContains(response,'autoplay muted playsinline')
            self.assertContains(response,'data-mobile-url="/scene-media/'+str(self.doc.pk)+'/?v=')
            self.assertContains(response,'/quote/?lang='+lang)
            self.assertContains(response,'construction-scene.js')
            self.assertNotContains(response,'<video loop')
            self.assertNotContains(response,'<source src="/scene-media/')
        self.brand.scene_caption_en='Reviewed concept caption';self.brand.save(update_fields=['scene_caption_en'])
        self.assertContains(self.client.get('/en/'),'Reviewed concept caption')

    def test_disabled_or_missing_assets_fall_back_to_original_hero(self):
        for field,value in [('scene_enabled',False),('scene_video',None),('scene_poster',None)]:
            original=getattr(self.brand,field);setattr(self.brand,field,value);self.brand.save()
            self.assertNotContains(self.client.get('/ar/'),'data-construction-scene')
            self.assertEqual(self.client.get(f'/scene-media/{self.doc.pk}/').status_code,404)
            setattr(self.brand,field,original)

    def test_selected_video_range_head_and_unselected_denial(self):
        url=f'/scene-media/{self.doc.pk}/'
        response=self.client.get(url,HTTP_RANGE='bytes=8-19')
        self.assertEqual(response.status_code,206)
        self.assertEqual(b''.join(response.streaming_content),self.bytes[8:20])
        self.assertEqual(response['Content-Range'],f'bytes 8-19/{len(self.bytes)}')
        suffix=self.client.get(url,HTTP_RANGE='bytes=-10')
        self.assertEqual(b''.join(suffix.streaming_content),self.bytes[-10:])
        head=self.client.head(url);self.assertEqual(int(head['Content-Length']),len(self.bytes))
        self.assertEqual(head.content,b'')
        self.assertEqual(self.client.get(url,HTTP_RANGE='bytes=9999-').status_code,416)
        self.assertEqual(self.client.get(url,HTTP_RANGE='bytes=0-1,3-4').status_code,416)
        other=get_document_model().objects.create(title='Unselected',file=SimpleUploadedFile('other.mp4',self.bytes))
        self.assertEqual(self.client.get(f'/scene-media/{other.pk}/').status_code,404)
        self.assertEqual(self.client.get('/media/documents/scene.mp4').status_code,404)

    def test_restricted_collection_cannot_be_exposed_by_settings_or_video_route(self):
        collection=Collection.get_first_root_node().add_child(name='Private fixture')
        CollectionViewRestriction.objects.create(collection=collection,restriction_type='login')
        self.doc.collection=collection;self.doc.save()
        self.brand.refresh_from_db()
        with self.assertRaises(ValidationError):self.brand.clean()
        self.assertNotContains(self.client.get('/ar/'),'data-construction-scene')
        self.assertEqual(self.client.get(f'/scene-media/{self.doc.pk}/').status_code,404)

    def test_model_validation_rejects_missing_assets_and_renamed_non_video(self):
        self.brand.scene_poster=None
        with self.assertRaises(ValidationError):self.brand.clean()

        self.brand.scene_poster=self.poster
        self.brand.scene_video=get_document_model().objects.create(title='Invalid',file=SimpleUploadedFile('invalid.mp4',b'<html>not MP4</html>'))
        with self.assertRaises(ValidationError):self.brand.clean()

    def test_owner_panel_renders_enable_video_and_poster_controls(self):
        owner=get_user_model().objects.create_superuser('scene-panel-owner','panel@example.test','synthetic-only')
        self.client.force_login(owner)
        response=self.client.get(reverse('wagtailsettings:edit',args=['home','brandsettings']),follow=True)
        self.assertEqual(response.status_code,200)
        for name in ['scene_enabled','scene_video','scene_video_mobile','scene_poster','scene_poster_mobile']:
            self.assertContains(response,'name="'+name+'"')

    def test_import_preview_and_existing_configuration_do_not_reset_owner_work(self):
        user=get_user_model().objects.create_superuser('scene-owner','owner@example.test','synthetic-only')
        page=ContentPage.objects.get(slug='anb-new-tower',locale__language_code='en')
        revision=page.save_revision(user=user)
        before=list(HomePage.objects.values_list('pk','latest_revision_id'))
        documents=get_document_model().objects.count()
        output=io.StringIO();call_command('install_construction_scene',stdout=output)
        self.assertIn('preserved',output.getvalue())
        call_command('install_construction_scene',apply=True,enable=True,stdout=io.StringIO())
        self.assertEqual(get_document_model().objects.count(),documents)
        self.assertEqual(before,list(HomePage.objects.values_list('pk','latest_revision_id')))
        page.refresh_from_db();self.assertEqual(page.latest_revision_id,revision.pk)

    def test_initial_import_is_once_only_even_after_owner_clears_settings(self):
        for field in ['scene_video','scene_video_mobile','scene_poster','scene_poster_mobile']:setattr(self.brand,field,None)
        self.brand.scene_enabled=False;self.brand.save()
        root=Path(self.temp.name)/'assets'/'construction-scene';root.mkdir(parents=True)
        for name in ['desktop.mp4','mobile.mp4']:(root/name).write_bytes(self.bytes)
        for name in ['poster.jpg','poster-mobile.jpg']:
            with self.poster.file.open('rb') as file:(root/name).write_bytes(file.read())
        with override_settings(BASE_DIR=Path(self.temp.name)):
            call_command('install_construction_scene',apply=True,enable=True,stdout=io.StringIO())
            self.brand.refresh_from_db();self.assertTrue(self.brand.construction_scene_ready)
            self.brand.scene_enabled=False;self.brand.scene_poster=None;self.brand.save()
            count=get_document_model().objects.count()
            call_command('install_construction_scene',apply=True,enable=True,stdout=io.StringIO())
            self.brand.refresh_from_db();self.assertFalse(self.brand.scene_enabled);self.assertIsNone(self.brand.scene_poster)
            self.assertEqual(get_document_model().objects.count(),count)
