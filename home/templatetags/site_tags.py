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
    return ContentPage.objects.live().public().filter(depth=3, **locale).exclude(slug__in=['privacy','terms','cookies']).order_by('path')

@register.simple_tag
def curated_cards(locale, value):
    chosen=value.get('selected_pages') or []
    if chosen:
        ids=[p.pk for p in chosen if p]
        pages={p.pk:p for p in ContentPage.objects.live().public().filter(pk__in=ids,locale=locale,kind=value['kind']).select_related('hero_image')}
        return [pages[i] for i in ids if i in pages]
    return cards(locale,value['kind'],value['count'])

@register.simple_tag
def policy_pages(language):
    return ContentPage.objects.live().public().filter(slug__in=['privacy','terms','cookies'],locale__language_code=language).order_by('slug')

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

@register.simple_tag(takes_context=True)
def menu_target(context, language, target):
    if not target: return None
    # One public-page map per request, rather than a translation/restriction query
    # for every navigation/footer link. public() also excludes restricted ancestors.
    request=context.get('request')
    cache=getattr(request,'_kfata_menu_pages',{}) if request else {}
    if language not in cache:
        from wagtail.models import Page
        cache[language]={p.translation_key:p for p in Page.objects.live().public().filter(locale__language_code=language)}
        if request is not None:request._kfata_menu_pages=cache
    return cache[language].get(target.translation_key)

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
