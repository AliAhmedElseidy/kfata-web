"""Source-reviewed copy only. No raw PDFs, legal IDs, unsupported metrics or new photos."""
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Locale
from home.models import BrandSettings, ContentPage, ImportedImage
from .seed_content import Command as SeedCommand


# Profile page references are documented in docs/SOURCE_REVIEW.md.
PROJECTS = [
    ('anb-old-head-office','المقر الرئيسي القديم — ANB','ANB old head office','تجديد مساحات المقر الرئيسي القديم كما يرد في ملف الشركة.','Renovation of spaces in the old head office, documented in the company profile.'),
    ('anb-al-awali','فرع العوالي — ANB','ANB Al Awali branch','أعمال تجديد وتجهيز لفرع مصرفي ضمن معرض أعمال الشركة.','Bank branch renovation and fit-out documented in the company portfolio.'),
    ('anb-al-majmaah','فرع المجمعة — ANB','ANB Al Majmaah branch','تجديد مساحات الفرع وواجهته كما يعرضها البروفايل.','Branch interior and exterior renovation shown in the company profile.'),
    ('anb-southern-branches','تجديد الفروع الجنوبية — ANB','ANB southern branch renovation','أعمال تجديد لفروع مصرفية في المنطقة الجنوبية.','Renovation work across banking branches in the southern region.'),
    ('anb-atm-sites','مواقع الصراف الآلي — ANB','ANB ATM sites','إنشاء وتجهيز مواقع صراف آلي مستقلة وصرافات خدمة السيارات.','Construction and fit-out of standalone and drive-through ATM sites.'),
    ('telemoney-centres','مراكز التحويل — تلي موني','TeleMoney centres','إنشاء وتشطيب مساحات مراكز التحويل ضمن معرض الأعمال.','Construction and finishing of remittance-centre spaces in the portfolio.'),
    ('anb-courtyard','الساحات الخارجية — ANB','ANB courtyard works','أعمال تجديد وتنسيق لمساحات خارجية ضمن مشروعات الشركة.','Renovation and landscaping of outdoor spaces documented in the profile.'),
    ('amnco-cash-centre','مركز نقد — أمنكو','AMNCO cash centre','أعمال إنشاء وتشطيبات لمبنى مركز نقد كما يرد في الملف.','Cash-centre construction and finishing documented in the company profile.'),
    ('office-fitout','تجهيز المساحات المكتبية','Office fit-out','أعمال إنشاء وتشطيب وتجهيز لمساحات مكتبية.','Construction, finishing and fit-out of office spaces.'),
    ('restaurant-fitout','تشطيبات المطاعم والمقاهي','Restaurant and café fit-out','تشطيبات وتجهيز مساحات مطاعم ومقاهٍ ضمن معرض الأعمال.','Finishing and fit-out of restaurant and café spaces shown in the portfolio.'),
    ('school-muzahmiyah','مشروع مدرسة — المزاحمية','School project in Al Muzahmiyah','أعمال إنشاء وتشطيبات لمبنى مدرسي كما يعرضه ملف الشركة.','School-building construction and finishing shown in the company profile.'),
    ('al-ghat-landmark','مجسم الغاط الجمالي','Al Ghat architectural landmark','إنشاء وتشطيبات لمعلم معماري جمالي في الغاط.','Construction and finishing of an architectural landmark in Al Ghat.'),
    ('rumah-landmark','مجسم رماح الجمالي','Rumah architectural landmark','إنشاء وتشطيبات لمعلم معماري جمالي في رماح.','Construction and finishing of an architectural landmark in Rumah.'),
    ('road-works','أعمال الطرق','Road works','أعمال إنشاء وتشطيب للطرق ضمن معرض مشروعات الشركة.','Road construction and finishing documented in the company portfolio.'),
    ('warehouse-finishing','تشطيبات مستودع صناعي','Industrial warehouse finishing','أعمال تشطيبات لمستودع صناعي كما يرد في البروفايل.','Finishing works for an industrial warehouse shown in the profile.'),
]


class Command(BaseCommand):
    help = 'Import reviewed source copy and original wordmark; extra project pages stay drafts.'

    @transaction.atomic
    def handle(self, **options):
        ar=Locale.objects.get(language_code='ar');en=Locale.objects.get(language_code='en')
        parents=[ContentPage.objects.get(slug='projects',locale=loc) for loc in [ar,en]]
        helper=SeedCommand()
        for slug,at,et,asu,esu in PROJECTS:
            helper.pair(parents,ar,en,slug,at,et,kind='project',summaries=(asu,esu),publish=False)
        for lang in ['ar','en']:
            arabic=lang=='ar'
            self.fill(lang,'about',
                'خبرات تجمع التصميم والإنشاء والتجديد والتجهيز.' if arabic else 'Expertise connecting design, construction, renovation and fit-out.',
                'تقدم KFATA خدمات التصميم والتنفيذ والمقاولات والتجديد وتنسيق المواقع والتجهيزات والأنظمة التقنية. يعرض ملف الشركة أعمالًا في المساحات المصرفية والتجارية والمكتبية والسكنية، إلى جانب منشآت تعليمية وصناعية وأعمال طرق ومساحات خارجية.' if arabic else 'KFATA provides design and build, contracting, renovation, landscaping, furnishing and technical systems services. The company portfolio documents banking, commercial, office and residential spaces, alongside educational and industrial facilities, roads and outdoor works.')
            self.fill(lang,'quality-safety',
                'الجودة والسلامة والاستدامة' if arabic else 'Quality, safety and sustainability',
                'يصف ملف الشركة نهجًا يجمع إدارة الجودة ودقة التنفيذ مع ممارسات الصحة والسلامة المهنية وتقييم المخاطر وكفاءة استخدام الموارد. تبقى هذه الصفحة مسودة إلى حين مراجعة السياسة الحالية وتحديد الملفات المعتمدة للنشر؛ لم تُنشر أختام أو نسخ شهادات اعتماد.' if arabic else 'The company profile describes quality management and execution precision alongside health and safety practices, risk assessment and resource efficiency. This page remains a draft pending review of current policy and approved supporting documents; certificate seals and scans have not been published.')
            self.fill(lang,'anb-new-tower',
                'تجديد المساحات المصرفية والمكتبية' if arabic else 'Renovation of banking and office spaces',
                'يعرض ملف الشركة أعمال تجديد ضمن مبنى البرج، تشمل مساحات عمل داخلية وتجهيزاتها. تُحجب المساحات التعاقدية ومدد التنفيذ وبيانات التسليم إلى حين اعتمادها.' if arabic else 'The company profile documents renovation within the tower, including interior workspaces and their fit-out. Contract areas, delivery dates and programme details remain withheld pending approval.')
            self.fill(lang,'residential-villas',
                'إنشاء وتشطيبات سكنية' if arabic else 'Residential construction and finishing',
                'يعرض ملف الشركة أعمال إنشاء وتشطيب لفلل سكنية، تشمل الواجهات والمساحات الداخلية. تُعرض الصورة المعتمدة فقط؛ لا تُنشر بيانات أصحاب العقارات أو عناوينهم التفصيلية.' if arabic else 'The company profile presents residential villa construction and finishing, including facades and interior spaces. Only the approved photograph is published; homeowner details and precise property addresses are withheld.')
        # Two source pages disagree on branch identification. Keep the original revision for review.
        for p in ContentPage.objects.filter(slug='anb-golden-belt'):
            revision=p.get_latest_revision()
            if p.live and not (revision and revision.user_id): p.unpublish()
        logo_path=Path(settings.BASE_DIR)/'assets'/'kfata-logo.png'
        brand=BrandSettings.load()
        if logo_path.exists() and not brand.logo_id:
            source=ImportedImage.objects.filter(source_key='kfata-logo').select_related('image').first()
            logo=source.image if source else None
            if not logo:
                with logo_path.open('rb') as stream:
                    logo=get_image_model().objects.create(title='KFATA — source profile wordmark',file=File(stream,name='kfata-logo.png'))
                ImportedImage.objects.update_or_create(source_key='kfata-logo',defaults={'image':logo})
            brand.logo=logo;brand.save(update_fields=['logo'])
        self.stdout.write(self.style.SUCCESS('Source copy imported; 15 bilingual project groups remain drafts. Existing editor content and logo selections preserved.'))

    def fill(self, language, slug, title, text):
        p=ContentPage.objects.filter(locale__language_code=language,slug=slug).first()
        if not p or p.body: return
        latest=p.get_latest_revision()
        if latest and latest.user_id: return
        live=p.live
        p.body=[('heading',{'eyebrow':'KFATA','title':title,'text':'<p>'+text+'</p>'})]
        revision=p.save_revision()
        if live: revision.publish()
