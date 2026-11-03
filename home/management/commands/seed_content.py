from pathlib import Path
from urllib.parse import urlparse
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Locale, Page, Site
from home.models import HomePage, ContentPage, BrandSettings

class Command(BaseCommand):
    help = 'Create initial bilingual KFATA content without overwriting existing edited content.'
    @transaction.atomic
    def handle(self, **options):
        root = Page.get_first_root_node()
        ar,_ = Locale.objects.get_or_create(language_code='ar')
        en,_ = Locale.objects.get_or_create(language_code='en')
        images = {}
        for name in ['anb-interior','anb-facade','anb-tower','residential']:
            image = get_image_model().objects.filter(title='KFATA / '+name).first()
            if not image and (settings.BASE_DIR/'assets'/(name+'.jpg')).exists():
                with (settings.BASE_DIR/'assets'/(name+'.jpg')).open('rb') as f:
                    image = get_image_model().objects.create(title='KFATA / '+name, file=File(f,name=name+'.jpg'))
            images[name] = image
        home = HomePage.objects.filter(slug='ar', depth=2).first()
        if not home:
            default = HomePage.objects.filter(slug='home', headline='').first()
            if default:
                home=default; home.slug='ar';home.locale=ar
            else:
                home = HomePage(title='الرئيسية',slug='ar',locale=ar)
                root.add_child(instance=home)
            home.title='الرئيسية';home.headline='رؤية تُصمَّم.\nوإتقانٌ يُبنى.'
            home.introduction='من الإنشاء إلى أدق تفاصيل التشطيب. حلول متكاملة للمشروعات المصرفية والتجارية والسكنية في المملكة العربية السعودية.'
            home.hero_image=images['anb-interior']
            home.search_description='كفاتا العالمية للمقاولات: تعرّف على الخدمات والمشروعات في القطاعات المصرفية والتجارية والسكنية.'
            home.save_revision().publish()
        english = home.get_translation_or_none(en)
        if not english:
            english=home.copy_for_translation(en)
            english.slug='en';english.title='Home';english.headline='Vision, designed.\nExcellence, built.'
            english.introduction='From construction to the finest finishing detail. Integrated solutions for banking, commercial and residential projects in Saudi Arabia.'
            english.search_description='Explore KFATA International Contracting services and projects across banking, commercial and residential sectors.'
            english.save_revision().publish()
        definitions=[
            ('about','عن الشركة','About KFATA','page','','خبرات تتكامل من الفكرة إلى التسليم.','Expertise that connects vision with delivery.'),
            ('services','خدماتنا','Our expertise','listing','service','التصميم والتنفيذ والمقاولات والتجديد والتجهيز.','Design, construction, renovation and furnishing.'),
            ('sectors','القطاعات','Sectors','listing','sector','خبرات تخدم احتياجات قطاعات متنوعة.','Expertise across a range of sectors.'),
            ('projects','المشروعات','Projects','listing','project','نماذج من الأعمال الواردة في معرض مشروعات الشركة.','Selected work from the company portfolio.'),
            ('contact','تواصل معنا','Contact us','page','','حدّثنا عن مشروعك القادم.','Tell us about your next project.'),
        ]
        parents={}
        for slug,at,et,kind,listing,asu,esu in definitions:
            pair=[]
            for parent,loc,title,summary in [(home,ar,at,asu),(english,en,et,esu)]:
                p=ContentPage.objects.child_of(parent).filter(slug=slug).first()
                if not p:
                    p=ContentPage(title=title,slug=slug,locale=loc,kind=kind,listing_kind=listing,summary=summary,show_quote_form=slug=='contact')
                    if pair: p.translation_key=pair[0].translation_key
                    parent.add_child(instance=p);p.save_revision().publish()
                pair.append(p)
            parents[slug]=pair
        services=[('design-build','التصميم والتنفيذ','Design & build','حلول تجمع التصميم والتنفيذ في مسار متكامل.','Integrated design and delivery.'),('contracting','المقاولات والإنشاءات','Construction','تنفيذ الأعمال الإنشائية ضمن نطاق المشروع المتفق عليه.','Construction delivery aligned with the agreed project scope.'),('renovation','التجديد والتشطيبات','Renovation & finishing','تطوير المساحات وتجديد التشطيبات لتناسب احتياجات الاستخدام.','Refurbishment and finishes tailored to the needs of each space.'),('landscaping','تنسيق المواقع','Landscaping','تنفيذ أعمال تنسيق المواقع والمساحات الخارجية.','Landscaping and external works.'),('furnishing','التأثيث والتجهيز','Furnishing','تجهيز المساحات والأثاث بما يلائم طبيعة المشروع.','Furnishing and fit-out for the needs of each project.'),('technology','الأنظمة التقنية والأمنية','IT, AV & security','خدمات الأنظمة التقنية والصوتيات والمرئيات والأمن كما وردت في بروفايل الشركة.','IT, audiovisual and security services listed in the company profile.')]
        for slug,at,et,asu,esu in services:
            self.pair(parents['services'], ar,en,slug,at,et,kind='service',summaries=(asu,esu))
        for slug,at,et in [('banking','القطاع المصرفي','Banking'),('commercial','التجاري','Commercial'),('education','التعليمي','Education'),('industrial','الصناعي','Industrial'),('residential','السكني','Residential'),('public-spaces','الطرق والمساحات العامة','Roads & public spaces')]:
            self.pair(parents['sectors'],ar,en,slug,at,et,kind='sector')
        for slug,at,et,key,sector,client in [('anb-golden-belt','البنك العربي الوطني — الحزام الذهبي','ANB — Al Hizam Al Thahabi','anb-facade',('مصرفي','Banking'),'ANB'),('anb-new-tower','البنك العربي الوطني — البرج الجديد','ANB — New Tower','anb-tower',('مصرفي','Banking'),'ANB'),('residential-villas','الفلل السكنية','Residential villas','residential',('سكني','Residential'),'')]:
            pages=self.pair(parents['projects'],ar,en,slug,at,et,kind='project',hero_image=images[key],client=client,sectors=sector)
            if key=='anb-facade' and images['anb-interior']:
                for p in pages:
                    if not p.body:
                        p.body=[('gallery',{'title':'','images':[{'image':images['anb-interior'],'caption':''}]})];p.save_revision().publish()
        # Editorial/legal sections remain drafts pending company-approved information.
        for slug,at,et in [('quality-safety','الجودة والسلامة','Quality & safety'),('certifications','الشهادات والاعتمادات','Certifications'),('news','الأخبار والمعرفة','News & insights'),('careers','الوظائف','Careers'),('privacy','سياسة الخصوصية','Privacy policy')]:
            self.pair([home,english],ar,en,slug,at,et,kind='page',publish=False)
        for idx,p in enumerate([home,english]):
            if not p.body:
                p.body=[('heading',{'eyebrow':'BUILT AROUND YOUR VISION','title':['نبني المساحات التي تنمو فيها الأعمال.','We build spaces where business grows.'][idx],'text':['<p>خبرات تجمع الإنشاءات والتصميم والتجهيز لمشروعات متنوعة في المملكة العربية السعودية.</p>','<p>Construction, design and fit-out expertise for diverse projects across Saudi Arabia.</p>'][idx]}),('listing',{'title':['المشروعات تتحدث عنّا.','Our work speaks for itself.'][idx],'kind':'project','count':3}),('image_text',{'title':['خبرات من الرؤية إلى التنفيذ.','From vision to execution.'][idx],'text':['<p>تعرّف على خدماتنا في التصميم والإنشاءات والتجديد والتجهيز.</p>','<p>Explore our design, construction, renovation and furnishing expertise.</p>'][idx],'image':images['anb-interior'],'reverse':False}),('listing',{'title':['خبرات تتكامل.','Integrated expertise.'][idx],'kind':'service','count':6}),('cta',{'title':['كل مشروع كبير يبدأ برؤية.','Every great project starts with a vision.'][idx],'text':['شاركنا تفاصيل مشروعك القادم.','Tell us about your next project.'][idx],'button_label':['اطلب عرض سعر','Request a quote'][idx],'page':None})]
                if not images['anb-interior']:
                    p.body = [(block.block_type, block.value) for block in p.body if block.block_type != 'image_text']
                p.cta_label=['استكشف مشروعاتنا','Explore our projects'][idx];p.cta_page=parents['projects'][idx];p.save_revision().publish()
        url=urlparse(settings.PUBLIC_BASE_URL)
        site=Site.objects.filter(is_default_site=True).first() or Site()
        site.hostname=url.hostname;site.port=url.port or (443 if url.scheme=='https' else 80);site.root_page=root;site.site_name='KFATA';site.is_default_site=True;site.save()
        BrandSettings.load()
        self.stdout.write(self.style.SUCCESS('Initial bilingual content created. Existing edited content was preserved. Review drafts and contact information before production indexing.'))
    def pair(self, parents, ar,en,slug,at,et,kind,summaries=('',''),sectors=('',''),publish=True,**fields):
        result=[]
        for idx,(parent,loc,title) in enumerate(zip(parents,[ar,en],[at,et])):
            p=ContentPage.objects.child_of(parent).filter(slug=slug).first()
            if not p:
                p=ContentPage(title=title,slug=slug,locale=loc,kind=kind,summary=summaries[idx],sector=sectors[idx],**fields)
                if result:p.translation_key=result[0].translation_key
                parent.add_child(instance=p)
                revision=p.save_revision()
                if publish: revision.publish()
                else: p.live=False;p.save(update_fields=['live'])
            result.append(p)
        return result
