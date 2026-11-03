import json
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from home.models import ContentPage
register = template.Library()

@register.simple_tag
def cards(locale, kind, count=6):
    return ContentPage.objects.live().public().filter(locale=locale, kind=kind).select_related('hero_image').order_by('-first_published_at')[:count]

@register.simple_tag
def navigation(page):
    return ContentPage.objects.live().public().filter(locale=page.locale, depth=3).order_by('path')

@register.simple_tag
def organization_json(brand, lang):
    data = {'@context':'https://schema.org','@type':'Organization','name':brand.company_ar if lang=='ar' else brand.company_en,'url':settings.PUBLIC_BASE_URL}
    if brand.phone: data['telephone'] = brand.phone
    if brand.email: data['email'] = brand.email
    if brand.linkedin: data['sameAs'] = [brand.linkedin]
    return mark_safe(json.dumps(data, ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026'))

@register.simple_tag
def translated_nav(page, target):
    return target.get_translation_or_none(page.locale) or target

@register.simple_tag
def privacy_page(language):
    return ContentPage.objects.live().public().filter(slug='privacy', locale__language_code=language).first()
