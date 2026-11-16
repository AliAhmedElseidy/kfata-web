from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp
from io import StringIO

from django.core.management import call_command


class SecurityPolicyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", stdout=StringIO())
        cls.owner = get_user_model().objects.create_superuser("security-test", password="test-only-password")

    def test_public_csp_has_fresh_nonce_and_admin_rolls_out_in_report_only(self):
        first = self.client.get("/ar/")
        second = self.client.get("/ar/")
        self.assertEqual(first.status_code, 200)
        policy = first["Content-Security-Policy"]
        self.assertIn("media-src 'self' blob:", policy)
        self.assertIn("object-src 'none'", policy)
        self.assertNotEqual(policy, second["Content-Security-Policy"])
        nonce = first.wsgi_request.csp_nonce
        self.assertIn(f"'nonce-{nonce}'", policy)
        self.assertContains(first, f'<style nonce="{nonce}">')
        login = self.client.get(reverse("wagtailadmin_login"))
        self.assertIn("no-store", login["Cache-Control"])
        self.assertIn("Content-Security-Policy-Report-Only", login)
        self.assertNotIn("script-src", login["Content-Security-Policy"])
        self.assertEqual(self.client.get("/media/images/file.svg").status_code, 404)

    def test_owner_can_enrol_without_lockout_and_confirmed_otp_guards_private_routes(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        enroll = reverse("wagtail_2fa_device_new")
        self.assertEqual(self.client.get(enroll).status_code, 200)
        device = TOTPDevice.objects.create(user=self.owner, confirmed=True)
        challenge = reverse("wagtail_2fa_auth")
        self.assertTrue(self.client.get("/admin/")["Location"].startswith(challenge))
        self.assertTrue(self.client.get("/private/enquiry/1/")["Location"].startswith(challenge))
        self.assertEqual(self.client.get(challenge).status_code, 200)
        token = str(totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits)).zfill(device.digits)
        result = self.client.post(challenge, {"otp_token": token, "otp_device": device.persistent_id, "next": "/admin/"})
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_invalid_upload_is_rejected_without_storage(self):
        from home.forms import EnquiryForm

        form = EnquiryForm(files={"attachment": SimpleUploadedFile("bad.png", b"not an image")}, data={})
        self.assertIn("attachment", form.errors)
