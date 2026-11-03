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

SERVICES = [
    ('design-build','التصميم والتنفيذ','Design and build','يجمع هذا المجال التخطيط التصميمي وأعمال التنفيذ ضمن نطاق يحدده المشروع. لبدء مناقشة النطاق، وضّح الاستخدام المطلوب ومرحلة التصميم الحالية وأي رسومات أو متطلبات متاحة.','This service connects design planning and construction within an agreed project scope. To discuss the scope, describe the intended use, current design stage and any available drawings or requirements.'),
    ('contracting','المقاولات والإنشاءات','Contracting and construction','تتضمن أعمال الشركة الموثقة إنشاء مبانٍ ومرافق وأعمال تشطيبات في قطاعات متنوعة. عند التواصل، حدد نوع الأعمال والموقع والمرحلة الحالية والمتطلبات المعروفة للمشروع.','The documented portfolio includes building and facility construction and finishing across several sectors. When contacting us, identify the work type, location, current stage and known project requirements.'),
    ('renovation','التجديد والتشطيبات','Renovation and finishing','يعرض ملف الأعمال تجديد مساحات مصرفية ومكتبية وتجارية وتطوير التشطيبات الداخلية والخارجية. شاركنا وصف المساحة القائمة والتغييرات المطلوبة وأي قيود تتعلق باستمرار التشغيل أثناء الأعمال.','The portfolio documents banking, office and commercial renovation and interior/exterior finishes. Share the existing space, proposed changes and any constraints on keeping the premises operational during the work.'),
    ('landscaping','تنسيق المواقع والمساحات الخارجية','Landscaping and external spaces','تظهر في ملف الشركة أعمال ساحات ومناطق خارجية ضمن نطاق المشروعات. يساعد تحديد طبيعة الموقع واستخدامه وأعماله المطلوبة على مناقشة نطاق تنسيق الموقع والتجهيزات الخارجية.','The company profile includes courtyard and outdoor-space works. Describing the site, its use and the required work helps define the landscaping and external-works scope.'),
    ('furnishing','التأثيث والتجهيز','Furnishing and fit-out','ترد التجهيزات والأثاث ضمن خدمات الشركة. حدد استخدام المساحة واحتياجات مناطق العمل والاستقبال والأثاث المطلوب وأي متطلبات قائمة عند مناقشة مشروع التجهيز.','Furnishings and fit-out are listed company services. Describe the use of the space, work and reception areas, furniture needs and existing requirements when discussing the fit-out.'),
    ('technology','الأنظمة التقنية والصوت والصورة والأمن','IT, AV and security systems','يشمل نطاق الخدمة المعلن الأنظمة التقنية والصوت والصورة وأنظمة الأمن والمراقبة. وضّح الأنظمة المطلوبة وما هو قائم منها ومتطلبات الربط والتشغيل؛ يتحدد نطاق التنفيذ والمتطلبات الفنية ضمن المشروع.','The listed scope covers IT, audiovisual, security and surveillance systems. Identify required and existing systems and their integration/operating needs; implementation and technical requirements are defined for each project.'),
]

SECTORS = [
    ('banking','القطاع المصرفي','Banking','يعرض الملف مشروعات تجديد مبانٍ وفروع مصرفية ومواقع صراف آلي ومراكز تحويل. تختلف متطلبات المساحات العامة ومناطق العمل والتجهيزات بحسب طبيعة كل منشأة ونطاقها.','The profile documents bank building/branch renovation, ATM sites and remittance centres. Public areas, workspaces and fit-out requirements depend on each facility and its agreed scope.'),
    ('commercial','القطاع التجاري والمكتبي','Commercial and offices','تشمل الأمثلة الواردة في الملف مساحات مكتبية ومطاعم ومقاهي ومرافق تجارية. يمكن مناقشة الإنشاء أو التجديد أو التشطيبات أو التجهيز وفق حالة الموقع ومتطلبات استخدامه.','Examples in the portfolio include offices, restaurants, cafés and commercial facilities. Construction, renovation, finishes or fit-out can be discussed according to the site and its intended use.'),
    ('education','القطاع التعليمي','Education','يتضمن ملف الشركة مشروع مبنى مدرسي وأعمال إنشاء وتشطيبات مرتبطة به. عند مناقشة منشأة تعليمية، حدد المرحلة الحالية للموقع ونطاق المباني والمرافق المطلوب العمل عليها.','The company profile includes school-building construction and finishing. For an educational facility, identify the current site stage and the buildings/facilities within the proposed scope.'),
    ('industrial','القطاع الصناعي','Industrial','يعرض الملف أعمال تشطيبات لمستودع صناعي. يعتمد تحديد نطاق العمل على استخدام المبنى ومتطلبات المساحات التشغيلية والخدمات القائمة والأعمال المطلوب تنفيذها.','The profile presents industrial warehouse finishing. Scope depends on building use, operational areas, existing services and the required work.'),
    ('residential','القطاع السكني','Residential','تشمل أعمال الشركة الموثقة إنشاء وتشطيب فلل سكنية وواجهاتها ومساحاتها الداخلية. شاركنا مرحلة المشروع ومتطلبات المساحات والتشطيبات عند التواصل، دون إرسال بيانات شخصية أو عناوين تفصيلية غير لازمة.','Documented residential work includes villa construction and finishing, facades and interior spaces. Share the project stage, space and finish requirements without unnecessary personal information or precise private addresses.'),
    ('public-spaces','الطرق والساحات والمساحات العامة','Roads, plazas and public spaces','يتضمن الملف أعمال طرق وساحات ومعالم معمارية جمالية. يحدد نوع الموقع واستخدامه والأعمال المدنية والتشطيبات المطلوبة نطاق المشروع المقترح.','The portfolio includes roads, plazas and architectural landmarks. Site use, civil works and finishing requirements define the proposed scope.'),
    ('entertainment','القطاع الترفيهي','Entertainment','يورد ملف الشركة القطاع الترفيهي ضمن القطاعات المستهدفة. عند التواصل بشأن مشروع من هذا النوع، حدد طبيعة المرفق واستخدام المساحات وحالة الموقع ونطاق الأعمال المطلوب مناقشته.','The company profile lists entertainment among its target sectors. Describe the facility, use of space, site stage and the scope you wish to discuss.'),
]


class Command(BaseCommand):
    help = 'Import reviewed source copy and original wordmark; extra project pages stay drafts.'

    @transaction.atomic
    def handle(self, **options):
        ar=Locale.objects.get(language_code='ar');en=Locale.objects.get(language_code='en')
        parents=[ContentPage.objects.get(slug='projects',locale=loc) for loc in [ar,en]]
        helper=SeedCommand()
        sector_parents=[ContentPage.objects.get(slug='sectors',locale=loc) for loc in [ar,en]]
        helper.pair(sector_parents,ar,en,'entertainment','القطاع الترفيهي','Entertainment',kind='sector',publish=False)
        for slug,at,et,asu,esu in PROJECTS:
            helper.pair(parents,ar,en,slug,at,et,kind='project',summaries=(asu,esu),publish=False)
        for lang in ['ar','en']:
            arabic=lang=='ar'
            for slug,at,et,ate,ete in SERVICES:
                self.fill(lang,slug,at if arabic else et,ate if arabic else ete)
            for slug,at,et,ate,ete in SECTORS:
                self.fill(lang,slug,at if arabic else et,ate if arabic else ete,publish=True)
            self.fill(lang,'sectors','مجالات العمل' if arabic else 'Areas of work','تعرّف على نطاق القطاعات الواردة في ملف الشركة، ثم شاركنا متطلبات مشروعك لتحديد الأعمال المناسبة.' if arabic else 'Explore the sectors listed in the company profile, then share your project requirements to define the appropriate scope.',publish=True)
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
        for lang in ['ar','en']:
            for project,sector,service in [('anb-new-tower','banking','renovation'),('residential-villas','residential','contracting')]:
                p=ContentPage.objects.get(slug=project,locale__language_code=lang)
                latest=p.get_latest_revision()
                if latest and latest.user_id: continue
                changed=False
                if not p.related_sectors.exists():
                    p.related_sectors.add(ContentPage.objects.get(slug=sector,kind='sector',locale=p.locale));changed=True
                if not p.related_services.exists():
                    p.related_services.add(ContentPage.objects.get(slug=service,kind='service',locale=p.locale));changed=True
                if not p.location:
                    p.location='الرياض' if lang=='ar' else 'Riyadh';changed=True
                if not p.scope:
                    p.scope=({'ar':'تجديد المساحات الداخلية','en':'Interior renovation'} if project=='anb-new-tower' else {'ar':'الإنشاء والتشطيبات','en':'Construction and finishing'})[lang];changed=True
                if changed:
                    revision=p.save_revision()
                    if p.live: revision.publish()
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

    def fill(self, language, slug, title, text, publish=False):
        p=ContentPage.objects.filter(locale__language_code=language,slug=slug).first()
        if not p: return
        latest=p.get_latest_revision()
        if latest and latest.user_id: return
        live=p.live
        changed=False
        if not p.summary:
            p.summary=text.split('. ')[0].rstrip('.')+'.';changed=True
        if not p.search_description:
            p.search_description=text[:160];changed=True
        if p.body:
            if changed:
                revision=p.save_revision()
                if live: revision.publish()
            return
        p.body=[('heading',{'eyebrow':'KFATA','title':title,'text':'<p>'+text+'</p>'})]
        revision=p.save_revision()
        if live or publish: revision.publish()
