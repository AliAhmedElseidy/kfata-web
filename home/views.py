import logging
import ipaddress
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import connection
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from django.utils.crypto import salted_hmac
from .forms import EnquiryForm
from .models import Enquiry, BrandSettings, ContentPage
logger = logging.getLogger(__name__)

@require_GET
def health(request):
    try:
        with connection.cursor() as cursor: cursor.execute('SELECT 1')
    except Exception:
        return JsonResponse({'status':'unavailable'}, status=503)
    return JsonResponse({'status':'ok'})

@require_GET
def robots(request):
    text = 'User-agent: *\nDisallow: /\n'
    if settings.SITE_INDEXABLE:
        text = f'User-agent: *\nDisallow: /admin/\nDisallow: /django-admin/\nDisallow: /private/\nDisallow: /quote/\nSitemap: {settings.PUBLIC_BASE_URL}/sitemap.xml\n'
        if not BrandSettings.load(request).allow_ai_training:
            text += '\nUser-agent: GPTBot\nDisallow: /\n\nUser-agent: Google-Extended\nDisallow: /\n'
    return HttpResponse(text, content_type='text/plain')

@require_http_methods(['GET','POST'])
def quote(request):
    lang = request.GET.get('lang', 'ar')
    if lang not in {'ar','en'}: lang = 'ar'
    brand = BrandSettings.load(request)
    privacy = ContentPage.objects.live().public().filter(slug='privacy',locale__language_code=lang).first()
    enabled = brand.enquiries_enabled and bool(brand.email and brand.phone and privacy)
    if not enabled:
        return render(request, 'home/quote.html', {'lang':lang, 'enquiries_unavailable':True}, status=503 if request.method == 'POST' else 200)
    form = EnquiryForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        # REMOTE_ADDR only: do not trust a user-provided X-Forwarded-For.
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        try:
            if any(ipaddress.ip_address(client_ip) in ipaddress.ip_network(net) for net in settings.TRUSTED_PROXY_NETWORKS):
                client_ip = str(ipaddress.ip_address(request.META.get('HTTP_X_REAL_IP', client_ip)))
        except ValueError:
            pass
        key = 'quote:' + salted_hmac('quote-rate', client_ip).hexdigest()
        count = cache.get(key, 0)
        if count >= 5:
            form.add_error(None, 'Too many requests. Please try again later.')
            return render(request, 'home/quote.html', {'form':form, 'lang':lang}, status=429)
        if not cache.add(key, 1, timeout=600):
            try: cache.incr(key)
            except ValueError: cache.set(key, 1, timeout=600)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.language = lang
            enquiry.save()
            if settings.EMAIL_HOST and settings.ENQUIRY_EMAIL:
                try:
                    send_mail('KFATA: new enquiry', f'A new enquiry #{enquiry.pk} is available in the admin. Sign in to review it.', settings.DEFAULT_FROM_EMAIL,[settings.ENQUIRY_EMAIL])
                    Enquiry.objects.filter(pk=enquiry.pk).update(notification_sent=True)
                except Exception:
                    logger.warning('Enquiry notification failed for enquiry %s', enquiry.pk)
            messages.success(request, 'تم استلام طلبك / Your enquiry has been received.')
            return redirect('/quote/?lang=' + lang)
    return render(request, 'home/quote.html', {'form':form, 'lang':lang, 'privacy':privacy})

@login_required(login_url='/admin/login/')
@permission_required('home.view_enquiry', raise_exception=True)
@require_GET
def attachment(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if not enquiry.attachment: raise Http404
    try: f = enquiry.attachment.open('rb')
    except FileNotFoundError: raise Http404
    response = FileResponse(f, as_attachment=True, filename='enquiry-attachment.jpg')
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

@require_GET
def public_image(request, path):
    if not path.startswith(('images/', 'original_images/', 'avatar_images/')) or '..' in path.split('/'):
        raise Http404
    try:
        f = default_storage.open(path, 'rb')
    except (FileNotFoundError, SuspiciousFileOperation):
        raise Http404
    response = FileResponse(f)
    response['Cache-Control'] = 'public, max-age=86400'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
