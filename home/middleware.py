from django.conf import settings

class IndexingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        smtp_settings=request.path.startswith('/admin/settings/home/smtpsettings/')
        if smtp_settings:
            request.sensitive_post_parameters='__ALL__'
        response = self.get_response(request)
        if smtp_settings:
            response['Cache-Control']='private, no-store'
        if not settings.SITE_INDEXABLE or request.path.startswith(('/admin/', '/django-admin/', '/quote/', '/private/', '/health/')):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
