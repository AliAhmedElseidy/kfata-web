import json
from urllib.parse import urljoin
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from home.models import ContentPage
register = template.Library()

@register.simple_tag
def cards(locale, kind, count=6):
    return ContentPage.objects.live().public().filter(locale=locale, kind=kind).select_related('hero_image').order_by('-first_published_at')[:count]

@register.simple_tag
def navigation(page=None, language='ar'):
    locale = {'locale':page.locale} if page else {'locale__language_code':language}
    return ContentPage.objects.live().public().filter(depth=3, **locale).exclude(slug='privacy').order_by('path')

@register.simple_tag
def organization_json(brand, lang):
    data = {'@context':'https://schema.org','@type':'GeneralContractor','@id':settings.PUBLIC_BASE_URL+'/#organization','name':brand.company_ar if lang=='ar' else brand.company_en,'url':settings.PUBLIC_BASE_URL,'areaServed':{'@type':'Country','name':'Saudi Arabia'}}
    if brand.phone: data['telephone'] = brand.phone
    if brand.email: data['email'] = brand.email
    if brand.linkedin: data['sameAs'] = [brand.linkedin]
    address=brand.address_ar if lang=='ar' else brand.address_en
    if address: data['address']=address
    if brand.logo_id: data['logo']=urljoin(settings.PUBLIC_BASE_URL,brand.logo.file.url)
    return mark_safe(json.dumps(data, ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026'))

@register.simple_tag
def translated_nav(page, target):
    if not target: return None
    return target.get_translation_or_none(page.locale) if page else target

@register.simple_tag
def menu_target(language, target):
    if not target: return None
    from wagtail.models import Locale
    locale = Locale.objects.filter(language_code=language).first()
    translated = target.get_translation_or_none(locale) if locale else None
    if translated and translated.live and not translated.get_view_restrictions().exists():
        return translated
    return None

@register.simple_tag
def page_schema(page):
    if not page: return '{}'
    ancestors = page.get_ancestors().live().public().filter(depth__gte=2).specific()
    items = [p for p in ancestors if p.full_url] + [page]
    data = {'@context':'https://schema.org', '@type':'BreadcrumbList', 'itemListElement':[
        {'@type':'ListItem','position':i,'name':p.title,'item':p.full_url} for i,p in enumerate(items,1)
    ]}
    if getattr(page,'kind',None) == 'article':
        data = {'@context':'https://schema.org','@graph':[data,{'@type':'Article','headline':page.title,'datePublished':page.first_published_at.isoformat() if page.first_published_at else '', 'dateModified':page.last_published_at.isoformat() if page.last_published_at else '', 'mainEntityOfPage':page.full_url}]}
    return mark_safe(json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026'))

@register.simple_tag
def privacy_page(language):
    return ContentPage.objects.live().public().filter(slug='privacy', locale__language_code=language).first()
