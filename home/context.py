from django.conf import settings
from .models import BrandSettings

def site_context(request):
    return {"brand": BrandSettings.load(request), "public_base": settings.PUBLIC_BASE_URL, "site_indexable": settings.SITE_INDEXABLE}
