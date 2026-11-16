import hashlib
import json
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from PIL import Image

from home.management.commands.import_kfata_2026 import load_source_pack
from home.models import ContentPage, ImportedImage


class Kfata2026SourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", stdout=StringIO())
        call_command("import_profile_drafts", stdout=StringIO())

    def run_import(self, **kwargs):
        result = StringIO()
        call_command("import_kfata_2026", stdout=result, **kwargs)
        return result.getvalue()

    @contextmanager
    def reviewed_test_images(self, filenames):
        with TemporaryDirectory() as temp:
            directory = Path(temp)
            reviews = {}
            for filename, color in filenames.items():
                path = directory / filename
                Image.new("RGB", (640, 480), color).save(path)
                reviews[filename] = {
                    "ar": "وصف الصورة", "en": "Photo description",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            manifest = directory / "manifest.json"
            manifest.write_text(json.dumps(reviews), encoding="utf-8")
            with patch("home.management.commands.import_kfata_2026.PHOTO_FILE", manifest):
                yield directory

    def test_pack_languages_and_attribution_safety(self):
        pack = load_source_pack()
        self.assertGreaterEqual(len(pack["pages"]), 9)
        for entry in pack["pages"]:
            self.assertTrue(entry["ar"]["body"])
            self.assertTrue(entry["en"]["body"])
        self.assertNotIn("anb-alhizam", pack["photo_groups"])
        self.assertIn("anb-alhizam", pack["review_only_photo_groups"])
        self.assertIn("al-wadi-offices", pack["photo_groups"])

    def test_dry_run_makes_no_changes_and_explicit_publish_required(self):
        before = (ContentPage.objects.count(), ImportedImage.objects.count())
        self.assertIn("PREVIEW ONLY", self.run_import())
        self.assertEqual((ContentPage.objects.count(), ImportedImage.objects.count()), before)
        with self.assertRaises(CommandError):
            self.run_import(publish=True)
        with self.assertRaises(CommandError):
            self.run_import(apply=True)

    def test_import_new_pages_gallery_and_idempotence(self):
        with self.reviewed_test_images({
            "residential-02.webp": "blue", "al-wadi-offices-02.webp": "white",
        }) as directory:
            self.assertIn("APPLIED", self.run_import(apply=True, publish=True, asset_dir=directory))
            ar = ContentPage.objects.get(slug="al-wadi-offices", locale__language_code="ar")
            en = ContentPage.objects.get(slug="al-wadi-offices", locale__language_code="en")
            self.assertTrue(ar.live)
            self.assertTrue(en.live)
            self.assertEqual(ar.translation_key, en.translation_key)
            self.assertTrue(ar.hero_image_id)
            self.assertTrue(ar.related_services.filter(slug="renovation").exists())
            self.assertTrue(ar.related_sectors.filter(slug="commercial").exists())
            self.assertTrue(any(block.block_type == "gallery" for block in ar.body))
            organizations = ContentPage.objects.get(slug="clients-partners", locale__language_code="ar")
            self.assertTrue(organizations.live)
            self.assertContains(self.client.get(ar.url), 'alt="وصف الصورة"')
            self.assertContains(self.client.get(en.url), 'alt="Photo description"')
            self.assertContains(self.client.get(en.url), 'hreflang="x-default"')
            villa = ContentPage.objects.get(slug="residential-villas", locale__language_code="ar")
            self.assertTrue(villa.hero_image_id)
            count = ContentPage.objects.count()
            gallery_count = sum(block.block_type == "gallery" for block in villa.body)
            self.assertIn("APPLIED", self.run_import(apply=True, publish=True, asset_dir=directory))
            villa.refresh_from_db()
            self.assertEqual(ContentPage.objects.count(), count)
            self.assertEqual(sum(block.block_type == "gallery" for block in villa.body), gallery_count)

    def test_owner_revision_is_not_replaced(self):
        with self.reviewed_test_images({"residential-02.webp": "green"}) as directory:
            villa = ContentPage.objects.get(slug="residential-villas", locale__language_code="ar")
            user = get_user_model().objects.create_superuser("kfata-owner-test", "owner@example.test", "test-only")
            revision = villa.save_revision(user=user)
            self.run_import(apply=True, publish=True, asset_dir=directory)
            villa.refresh_from_db()
            self.assertEqual(villa.latest_revision_id, revision.pk)

    def test_unreviewed_or_replaced_asset_is_rejected(self):
        with self.reviewed_test_images({"residential-02.webp": "green"}) as directory:
            path = directory / "residential-02.webp"
            Image.new("RGB", (640, 480), "white").save(path)
            with self.assertRaisesMessage(CommandError, "Image checksum differs"):
                self.run_import(asset_dir=directory)
            path.rename(directory / "anb-alhizam-01.webp")
            with self.assertRaisesMessage(CommandError, "Unreviewed image"):
                self.run_import(asset_dir=directory)
