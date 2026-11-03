from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap
from home import views

urlpatterns = [
    path('', RedirectView.as_view(url='/ar/', permanent=False), name='root'),
    path('media/<path:path>', views.public_image, name='public_image'),
    path('health/', views.health, name='health'),
    path('robots.txt', views.robots),
    path('sitemap.xml', sitemap),
    path('quote/', views.quote, name='quote'),
    path('private/enquiry/<int:pk>/', views.attachment, name='private_attachment'),
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
]
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [path('', include(wagtail_urls))]
