import logging
import secrets

import django_otp
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from django.utils.cache import add_never_cache_headers

logger = logging.getLogger("kfata.security")
ADMIN_PREFIXES = ("/admin/", "/django-admin/")
PRIVATE_PREFIXES = (*ADMIN_PREFIXES, "/private/", "/quote/")
MFA_EXEMPT = {
    "wagtailadmin_login", "wagtailadmin_logout", "kfata_otp_challenge",
    "wagtailadmin_javascript_catalog", "wagtailadmin_sprite",
}


class SecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(24)
        is_admin = request.path.startswith(ADMIN_PREFIXES)
        is_private = request.path.startswith(PRIVATE_PREFIXES)
        if is_private and request.method == "POST":
            request.sensitive_post_parameters = "__ALL__"
        response = self.get_response(request)
        if is_private:
            add_never_cache_headers(response)
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if response.get("Content-Type", "").startswith("text/html"):
            nonce = request.csp_nonce
            common = "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
            sources = (
                "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; "
                "font-src 'self'; connect-src 'self'; frame-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; style-src 'self' 'nonce-{nonce}'"
            )
            if is_admin:
                response["Content-Security-Policy"] = common
                response["Content-Security-Policy-Report-Only"] = sources + "; " + common
            else:
                response["Content-Security-Policy"] = sources + "; " + common
        if response.status_code >= 500:
            area = "admin" if is_admin else "enquiry" if request.path == "/quote/" else "public"
            logger.error("event=http_server_error area=%s status=%s", area, response.status_code)
        return response

    def process_view(self, request, view, args, kwargs):
        match = request.resolver_match
        if match and match.url_name in MFA_EXEMPT:
            return None
        if not request.path.startswith((*ADMIN_PREFIXES, "/private/", "/documents/")):
            return None
        user = request.user
        if user.is_authenticated and not user.is_verified() and django_otp.user_has_device(user, confirmed=True):
            return redirect_to_login(request.get_full_path(), login_url=reverse("kfata_otp_challenge"))
        return None
