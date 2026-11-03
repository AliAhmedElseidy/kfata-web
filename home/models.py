from django.core.validators import RegexValidator
from django.db import models
from wagtail import blocks
from .storage import private_storage
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page
from modelcluster.fields import ParentalManyToManyField
from .blocks import SiteBody

class ImportedImage(models.Model):
    """Stable provenance so renaming an image never duplicates the initial import."""
    source_key = models.CharField(max_length=80, unique=True)
    image = models.ForeignKey('wagtailimages.Image', null=True, on_delete=models.SET_NULL, related_name='+')

@register_setting
class BrandSettings(BaseGenericSetting):
    company_ar = models.CharField(max_length=150, default='KFATA')
    company_en = models.CharField(max_length=150, default='KFATA International Contracting')
    logo = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    favicon = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    accent = models.CharField(max_length=7, default='#c7a875', validators=[RegexValidator(r'^#[0-9a-fA-F]{6}$')])
    phone = models.CharField(max_length=30, blank=True)
    secondary_phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\d*$')], help_text='Country code and digits only; no + or spaces.')
    email = models.EmailField(blank=True)
    address_ar = models.CharField(max_length=250, blank=True)
    address_en = models.CharField(max_length=250, blank=True)
    map_url = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    animations = models.BooleanField(default=True)
    opening_animation = models.BooleanField(default=True)
    motion_level = models.CharField(max_length=10, choices=[('subtle','خفيف / Subtle'),('full','كامل / Full')], default='subtle')
    font = models.CharField(max_length=10, choices=[('tahoma','Tahoma'),('arial','Arial'),('serif','Georgia')], default='tahoma')
    background = models.CharField(max_length=7, default='#10191c', validators=[RegexValidator(r'^#[0-9a-fA-F]{6}$')])
    enquiries_enabled = models.BooleanField(default=False, help_text='Enable only after publishing reviewed privacy notices and company contact information.')
    privacy_version = models.CharField(max_length=20, default='2026-11-03')
    google_verification = models.CharField(max_length=150, blank=True)
    bing_verification = models.CharField(max_length=150, blank=True)
    allow_ai_training = models.BooleanField(default=False, help_text='Independent of search discovery; controls GPTBot and Google-Extended.')
    footer_menu = StreamField([('link', blocks.StructBlock([('page', blocks.PageChooserBlock()), ('label_ar', blocks.CharBlock()), ('label_en', blocks.CharBlock())]))], blank=True)
    menu = StreamField([('link', blocks.StructBlock([
        ('page', blocks.PageChooserBlock()),
        ('label_ar', blocks.CharBlock()),
        ('label_en', blocks.CharBlock()),
        ('children', blocks.ListBlock(blocks.StructBlock([('page', blocks.PageChooserBlock()), ('label_ar', blocks.CharBlock()), ('label_en', blocks.CharBlock())]), required=False)),
    ]))], blank=True)
    panels = [FieldPanel(f) for f in ['company_ar', 'company_en', 'logo', 'favicon', 'accent', 'phone', 'whatsapp', 'email', 'address_ar', 'address_en', 'map_url', 'linkedin', 'animations', 'opening_animation', 'menu']]
    panels += [FieldPanel(f) for f in ['motion_level','font','background','footer_menu','enquiries_enabled','google_verification','bing_verification','allow_ai_training']]
    panels += [FieldPanel('secondary_phone')]
    panels += [FieldPanel('privacy_version')]
    class Meta:
        verbose_name = 'هوية الموقع والتواصل / Brand and contact'

class HomePage(Page):
    eyebrow = models.CharField(max_length=180, default='KFATA INTERNATIONAL CONTRACTING')
    headline = models.CharField(max_length=200, blank=True)
    introduction = models.TextField(blank=True)
    hero_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    cta_label = models.CharField(max_length=80, blank=True)
    cta_page = models.ForeignKey('wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    body = StreamField(SiteBody(), blank=True)
    content_panels = Page.content_panels + [FieldPanel(f) for f in ['eyebrow','headline','introduction','hero_image','cta_label','cta_page','body']]
    promote_panels = Page.promote_panels + [FieldPanel('social_image')]
    subpage_types = ['home.ContentPage']
    max_count_per_parent = 2

class ContentPage(Page):
    KIND = [('page','صفحة / Page'),('service','خدمة / Service'),('sector','قطاع / Sector'),('project','مشروع / Project'),('article','مقال / Article'),('listing','فهرس / Listing')]
    kind = models.CharField(max_length=15, choices=KIND, default='page')
    summary = models.TextField(blank=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    related_services = ParentalManyToManyField('self', blank=True, symmetrical=False, limit_choices_to={'kind':'service'}, related_name='service_projects')
    related_sectors = ParentalManyToManyField('self', blank=True, symmetrical=False, limit_choices_to={'kind':'sector'}, related_name='sector_projects')
    hero_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    sector = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    client = models.CharField(max_length=150, blank=True)
    scope = models.CharField(max_length=250, blank=True)
    completed_year = models.PositiveSmallIntegerField(null=True, blank=True)
    listing_kind = models.CharField(max_length=15, choices=KIND, blank=True)
    show_quote_form = models.BooleanField(default=False)
    body = StreamField(SiteBody(), blank=True)
    content_panels = Page.content_panels + [FieldPanel('kind'),FieldPanel('summary'),FieldPanel('hero_image'),MultiFieldPanel([FieldPanel(f) for f in ['sector','location','client','scope','completed_year']], heading='بيانات المشروع / Project details'),FieldPanel('listing_kind'),FieldPanel('show_quote_form'),FieldPanel('body')]
    promote_panels = Page.promote_panels + [FieldPanel('social_image')]
    subpage_types = ['home.ContentPage']
    parent_page_types = ['home.HomePage','home.ContentPage']
    content_panels += [FieldPanel('related_services'), FieldPanel('related_sectors')]
    def get_context(self, request, *args, **kwargs):
        from django.core.paginator import Paginator
        context = super().get_context(request, *args, **kwargs)
        if self.kind == 'project':
            context['related_projects'] = ContentPage.objects.live().public().filter(locale=self.locale,kind='project',sector=self.sector).exclude(pk=self.pk).select_related('hero_image')[:3]
        elif self.kind in {'service','sector'}:
            field = 'related_services' if self.kind == 'service' else 'related_sectors'
            context['related_projects'] = ContentPage.objects.live().public().filter(locale=self.locale,kind='project',**{field:self}).select_related('hero_image')[:6]
        if self.listing_kind:
            qs = ContentPage.objects.live().public().filter(locale=self.locale, kind=self.listing_kind).select_related('hero_image').order_by('-first_published_at')
            sectors = list(qs.exclude(sector='').order_by('sector').values_list('sector', flat=True).distinct())
            selected = request.GET.get('sector','')
            if selected:
                qs = qs.filter(sector=selected)
            context.update(items=Paginator(qs, 9).get_page(request.GET.get('page')), sectors=sectors, selected_sector=selected)
        return context

class Enquiry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=8, default='ar')
    name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    service = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    attachment = models.FileField(upload_to='enquiries/%Y/%m/', storage=private_storage, blank=True)
    status = models.CharField(max_length=15, default='new', choices=[('new','جديد / New'),('contacted','تم التواصل / Contacted'),('closed','مغلق / Closed')])
    notes = models.TextField(blank=True)
    notification_sent = models.BooleanField(default=False)
    privacy_version = models.CharField(max_length=20, default='2026-11-03', editable=False)
    def __str__(self):
        return f'{self.name} — {self.created_at:%Y-%m-%d}'
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب عرض سعر / Enquiry'
