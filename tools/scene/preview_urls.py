"""Use only with preview_settings and runserver 127.0.0.1:8035."""
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.views.static import serve
from home.models import HomePage
from config.urls import urlpatterns as site_patterns


def preview(request, language):
    if not settings.DEBUG or language not in {'ar', 'en'}:
        raise Http404
    page = get_object_or_404(HomePage, locale__language_code=language, live=True)
    request.is_preview = True
    response = render(request, 'home/scene_preview.html', page.get_context(request))
    response['Cache-Control'] = 'no-store'
    if request.GET.get('nojs') == '1':
        response['Content-Security-Policy'] = "script-src 'none'"
    return response


def asset(request, name):
    if not settings.DEBUG or name not in {'poster.jpg', 'construction-preview.mp4'}:
        raise Http404
    return serve(request, name, document_root=settings.BASE_DIR / 'operations' / 'scene-preview')


urlpatterns = [
    path('scene-preview/<str:language>/', preview),
    path('scene-assets/<str:name>', asset),
] + site_patterns
