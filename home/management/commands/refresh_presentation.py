"""One-time owner-approved presentation update; preview by default.

Source: profile pp.2,4,5,6,22. Image/process/quality/WhatsApp approvals:
2026-11-04 conversation. Preserves editor revisions, SMTP and enquiries.
"""
from html import escape
from urllib.parse import quote
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.images import get_image_model
from home.models import HomePage,ContentPage,BrandSettings,ImportedImage,PresentationUpdate

KEY='presentation-2026-11-04-v1'
ASSETS={
 'engineering-illustration':('engineering-illustration.webp','صورة مولدة توضيحية للنشاط الهندسي / AI-generated engineering illustration'),
 'anb-workspace-1':('anb-workspace-1.jpg','مكاتب مشروع ANB — ملف الشركة ص6 / ANB workspace — profile p6'),
 'anb-workspace-2':('anb-workspace-2.jpg','مساحات عمل مشروع ANB — ملف الشركة ص6 / ANB workspaces — profile p6'),
 'residential-interior':('residential-interior.jpg','تشطيبات داخلية سكنية — ملف الشركة ص22 / Residential interior — profile p22'),
 'residential-courtyard':('residential-courtyard.jpg','فناء سكني — ملف الشركة ص22 / Residential courtyard — profile p22'),
}
SERVICES={
 'design-build':('التصميم والتنفيذ، برؤية واحدة.','Design and build, connected.','خدمة تربط التصور التصميمي بأعمال التنفيذ ضمن نطاق المشروع المتفق عليه. نناقش استخدام المساحة ومتطلباتها، والرسومات المتاحة، والمرحلة التي وصل إليها المشروع؛ ليبدأ الحوار من احتياج واضح.','A service connecting design intent with construction within the agreed project scope. Discuss space requirements, available drawings and the current project stage so the conversation starts with a clear brief.','استخدام المساحة ومتطلباتها؛ مرحلة التصميم؛ الرسومات المتاحة؛ الأعمال المراد تضمينها.','Space requirements; design stage; available drawings; work to be included.'),
 'contracting':('أعمال إنشاء تناسب طبيعة مشروعك.','Construction for your project.','تضم أعمال KFATA إنشاء مبانٍ ومرافق وتشطيبات في قطاعات متعددة، منها المباني السكنية والمنشآت التعليمية ومراكز النقد. يحدد نطاق كل مشروع الأعمال المطلوبة وحدود المسؤوليات والمتطلبات الفنية.','KFATA’s portfolio includes construction and finishing across residential buildings, educational facilities and cash centres. Each scope defines the works, responsibilities and technical requirements.','نوع المبنى؛ حالة الموقع؛ الرسومات والكميات إن وجدت؛ الأعمال المطلوبة.','Building type; site stage; drawings and quantities if available; required works.'),
 'renovation':('مساحات قائمة. إمكانات جديدة.','Existing spaces. New possibilities.','تشمل الأعمال تجديد مبانٍ وفروع مصرفية ومساحات مكتبية وتجارية، وتطوير التشطيبات الداخلية والخارجية. يبدأ تحديد النطاق بفهم الوضع القائم والتغييرات المرغوبة ومتطلبات استخدام المنشأة أثناء الأعمال.','Work includes bank building and branch refurbishment, office and commercial renovation, and interior and exterior finishes. Scope starts with existing conditions, intended changes and any operating requirements.','حالة المساحة؛ التغييرات المطلوبة؛ الأنظمة القائمة؛ قيود التشغيل والوصول.','Existing conditions; proposed changes; existing systems; operating and access constraints.'),
 'furnishing':('تجهيز يراعي استخدام المساحة.','Fit-out shaped around use.','التجهيزات والأثاث ضمن خدمات KFATA للمساحات التي تستقبل الأشخاص وتدعم أعمالهم اليومية. نناقش احتياجات مناطق العمل والاستقبال والتوزيع الداخلي والتجهيزات المطلوبة ضمن حدود المشروع.','Furnishing and fit-out are among KFATA’s services for spaces where people meet and work. Discuss workspace and reception needs, layouts and fittings within the project scope.','طبيعة الاستخدام؛ مناطق العمل والاستقبال؛ التجهيزات والأثاث المطلوب؛ المتطلبات القائمة.','Intended use; work and reception areas; required fittings and furniture; existing requirements.'),
 'landscaping':('المساحة الخارجية جزء من التجربة.','The outside is part of the experience.','تشمل أعمال الشركة ساحات ومساحات خارجية وتنسيق مواقع ضمن المشروعات. يساعد فهم استخدام الموقع وعلاقته بالمبنى والأعمال القائمة على تحديد نطاق الأعمال الخارجية المطلوبة.','The portfolio includes courtyards, external spaces and landscaping. Site use, its relationship to the building and existing works help define the external scope.','نوع الموقع؛ استخدام المساحات الخارجية؛ الأعمال القائمة؛ عناصر النطاق المطلوب.','Site type; use of external spaces; existing works; required scope elements.'),
 'technology':('أنظمة تتكامل مع احتياجات المكان.','Systems that fit the space.','تشمل خدمات KFATA المعلنة الأنظمة التقنية والصوت والصورة والأمن والمراقبة. يناقَش نطاق الأنظمة ومتطلبات الربط والتشغيل ضمن كل مشروع، بناءً على الاستخدام المطلوب وما هو قائم في الموقع.','KFATA’s listed services include IT, audiovisual, security and surveillance systems. Scope, integration and operating requirements are discussed for each project according to use and existing systems.','الأنظمة المطلوبة؛ الأنظمة القائمة؛ احتياجات الربط؛ متطلبات الاستخدام والتشغيل.','Required systems; existing systems; integration needs; use and operation requirements.'),
}

class Command(BaseCommand):
    help='Preview/apply the approved presentation update once, preserving editor revisions.'
    def add_arguments(self,parser): parser.add_argument('--apply',action='store_true')
    @transaction.atomic
    def handle(self,**options):
        self.images={x.source_key:x.image for x in ImportedImage.objects.select_related('image') if x.image_id}
        if not options['apply']:
            for p in list(HomePage.objects.all())+list(ContentPage.objects.filter(slug__in=list(SERVICES)+['about','anb-new-tower','residential-villas','quality-safety'])):
                self.stdout.write(f'{p.locale.language_code}/{p.slug}: '+('preserve existing revision' if not self.eligible(p) else 'eligible'))
            self.stdout.write('Dry run: no data changed. Use --apply after backup and review.');return
        for key,(filename,title) in ASSETS.items():
            if key not in self.images:
                path=settings.BASE_DIR/'assets'/filename
                if not path.exists(): raise CommandError('Missing approved asset: '+filename)
                with path.open('rb') as f: image=get_image_model().objects.create(title=title,file=File(f,name=filename))
                ImportedImage.objects.update_or_create(source_key=key,defaults={'image':image});self.images[key]=image
        for language in ['ar','en']:
            self.ar=language=='ar'
            home=HomePage.objects.get(locale__language_code=language,depth=2)
            self.pages={p.slug:p for p in ContentPage.objects.filter(locale=home.locale)}
            self.update_home(home)
            for slug,data in SERVICES.items():
                p=self.pages.get(slug)
                if p and self.eligible(p):
                    title=data[0 if self.ar else 1];text=data[2 if self.ar else 3];needs=data[4 if self.ar else 5]
                    p.summary=text.split('. ')[0].rstrip('.')+'.';p.search_description=p.summary[:160]
                    p.body=[self.heading(title,text,tone='stone'),self.heading(self.t('للبدء، شاركنا هذه المعلومات.','To start, share these details.'),needs),self.cta()]
                    image_key={'design-build':'anb-workspace-1','contracting':'residential','renovation':'anb-workspace-2','furnishing':'residential-interior','landscaping':'residential-courtyard'}.get(slug)
                    if not p.hero_image_id and image_key in self.images:p.hero_image=self.images[image_key]
                    self.save(p)
            self.update_about();self.update_projects();self.update_sectors();self.update_quality();self.policies(home)
        self.brand()
        self.stdout.write(self.style.SUCCESS('Approved presentation applied; editor revisions, SMTP and enquiries preserved.'))
    def t(self,a,e): return a if self.ar else e
    def eligible(self,p):
        if PresentationUpdate.objects.filter(page=p,key=KEY).exists() or (p.live and p.has_unpublished_changes):return False
        revision=p.get_latest_revision();return not (revision and revision.user_id)
    def save(self,p):
        p.save_revision().publish();PresentationUpdate.objects.get_or_create(page=p,key=KEY)
    def heading(self,title,text,tone='dark',eyebrow='KFATA'):
        return ('heading',{'visible':True,'tone':tone,'eyebrow':eyebrow,'title':title,'text':'<p>'+escape(text)+'</p>'})
    def cta(self):
        return ('cta',{'title':self.t('لنبدأ من تفاصيل مشروعك.','Let’s start with your project.'),'text':self.t('حدد الخدمة وموقع المشروع ومرحلته الحالية، وسنتواصل معك لمناقشة الاحتياج.','Share the service, project location and current stage so we can discuss your requirements.'),'button_label':self.t('اطلب عرض سعر','Request a quote'),'page':None})
    def listing(self,kind,title,slugs,tone='dark',intro=''):
        return ('listing',{'tone':tone,'title':title,'kind':kind,'count':len(slugs),'selected_pages':[self.pages[x] for x in slugs if x in self.pages],'introduction':intro})
    def process(self):
        steps=[('فهم الاحتياج','Understand the brief','نبدأ بنوع المشروع واستخدامه والمرحلة الحالية وما تتطلع إلى تنفيذه.','Start with the project type, intended use, current stage and required work.'),('مراجعة النطاق والمخططات','Review scope and drawings','نراجع المعلومات والمخططات المتاحة لتوضيح نطاق النقاش والمتطلبات.','Review available information and drawings to clarify scope and requirements.'),('الاتفاق على الأعمال','Agree the works','تحدد الأعمال والمسؤوليات والشروط في عرض السعر والعقد المعتمد.','Define the works, responsibilities and terms in the approved quotation and contract.'),('التنفيذ والتسليم','Build and hand over','تجري أعمال التنفيذ والتسليم وفق النطاق والشروط المتفق عليها.','Carry out construction and handover under the agreed scope and terms.')]
        return ('process',{'title':self.t('كيف نبدأ مشروعك؟','How does your project begin?'),'introduction':self.t('حوار واضح من أول احتياج إلى نطاق عمل متفق عليه.','A clear conversation from the initial brief to an agreed scope.'),'steps':[{'title':self.t(a,e),'text':self.t(at,et)} for a,e,at,et in steps]})
    def update_home(self,p):
        if not self.eligible(p):return
        p.headline=self.t('رؤيتك للمكان.\nخبرتنا في البناء.','Your vision for a place.\nOur expertise in building.')
        p.introduction=self.t('تصميم وإنشاء وتجديد وتجهيز للمساحات المصرفية والتجارية والسكنية. من متطلبات المشروع إلى تفاصيله المنفذة.','Design, construction, renovation and fit-out for banking, commercial and residential spaces. From project requirements to the details that bring them to life.')
        p.cta_label=self.t('استكشف مشروعاتنا','Explore our projects');p.secondary_cta_label=self.t('اطلب عرض سعر','Request a quote')
        p.body=[self.heading(self.t('مساحات تؤدي دورها.\nوتحمل رؤيتك.','Spaces that work.\nPlaces with purpose.'),self.t('تجمع KFATA التصميم والتنفيذ والمقاولات والتجديد والتجهيز. تتنوع أعمالها بين المساحات المصرفية والمكتبية والسكنية، إلى جانب منشآت تعليمية وصناعية وأعمال خارجية؛ ويبدأ كل نقاش باحتياجات المشروع ونطاقه.','KFATA brings together design and build, construction, renovation and fit-out. Its portfolio spans banking, office and residential spaces, alongside educational and industrial facilities and external works. Every conversation starts with the brief and scope.'),tone='stone',eyebrow='KFATA / PROFILE'),
         self.listing('project',self.t('أعمال تعكس ما نقدمه.','Work that shows what we do.'),['anb-new-tower','residential-villas'],intro=self.t('من تجديد مساحات العمل إلى إنشاء المباني السكنية وتشطيباتها.','From workspace renovation to residential construction and finishing.')),
         self.listing('service',self.t('خبرات مترابطة.\nللمشروع الذي تتصوره.','Connected expertise.\nFor the project you envision.'),list(SERVICES),tone='stone'),
         self.listing('sector',self.t('لكل قطاع متطلباته.','Every sector has its own requirements.'),['banking','commercial','residential','education','industrial','public-spaces','entertainment']),self.process(),
         ('image_text',{'tone':'stone','title':self.t('المخطط بداية.\nوالتفاصيل تصنع المكان.','A drawing is the start.\nDetails make the place.'),'text':'<p>'+self.t('تحتاج المشروعات إلى فهم التصميم وتنسيق أعمال الموقع والاهتمام بالتفاصيل. يجمع نشاط KFATA مجالات الإنشاء والتجديد والتجهيز؛ لتناقش متطلبات المشروع كوحدة مترابطة.','Projects call for understanding design, coordinating site work and attending to detail. KFATA’s work connects construction, renovation and fit-out so requirements can be discussed as an integrated whole.')+'</p>','image':self.images['engineering-illustration'],'caption':self.t('صورة مولدة توضيحية للنشاط الهندسي، وليست لفريق KFATA أو لأحد مشروعاتها.','AI-generated illustration of engineering activity; not KFATA staff or a KFATA project.'),'reverse':False}),
         self.heading(self.t('جودة التنفيذ تبدأ من التفاصيل.','Quality begins with the details.'),self.t('يعبر ملف الشركة عن الاهتمام بجودة التنفيذ ودقة التشطيبات. يناقش نطاق الجودة والسلامة ومتطلبات الموقع ضمن وثائق كل مشروع والأعمال المتفق عليها.','The company profile emphasizes workmanship and careful finishes. Project documents and the agreed scope define quality, safety and site requirements.'),eyebrow='KFATA / QUALITY'),self.faq(),self.cta()]
        self.save(p)
    def faq(self):
        items=[('ما المعلومات التي أرسلها لطلب عرض سعر؟','What should I share to request a quote?','نوع الخدمة وموقع المشروع ومرحلته الحالية ووصف الأعمال المطلوبة. يمكنك إرفاق صورة JPEG أو PNG حتى 5 ميجابايت. أرسل الحد اللازم من البيانات فقط.','Share the service, location, current stage and required work. You may attach one JPEG or PNG up to 5MB. Include only necessary information.'),('هل يمكن مناقشة تجديد مساحة قائمة؟','Can we discuss renovating an existing space?','نعم، تشمل أعمال الشركة تجديد مساحات مصرفية ومكتبية وتجارية. وضح حالة المساحة والتغييرات المطلوبة ومتطلبات استمرار التشغيل إن وجدت.','Yes. The portfolio includes banking, office and commercial renovation. Describe the conditions, changes and operating constraints.'),('هل طلب التواصل يمثل عرض سعر أو عقدًا؟','Does an enquiry constitute a quotation or contract?','طلب التواصل بداية لمناقشة الاحتياج. نطاق العمل والسعر والمدة والشروط تحدد في عرض سعر وعقد معتمدين.','An enquiry starts a discussion. Scope, price, schedule and terms are defined in an approved quotation and contract.'),('كيف أتابع طلبي أو بياناتي؟','How can I follow up on my enquiry or data?','تواصل على info@kfata.com أو الأرقام المنشورة، واذكر ما يساعد على تحديد طلبك دون إرسال وثائق هوية. توضح سياسة الخصوصية الاحتفاظ بالبيانات وحذفها.','Contact info@kfata.com or the published telephone numbers with enough information to identify your enquiry, without identity documents. The privacy notice explains retention and deletion.')]
        return ('faq',{'tone':'stone','title':self.t('قبل أن نبدأ.','Before we begin.'),'items':[{'question':self.t(a,e),'answer':self.t(at,et)} for a,e,at,et in items]})
    def update_about(self):
        p=self.pages.get('about')
        if not p or not self.eligible(p):return
        p.summary=self.t('تصميم ومقاولات وتجديد وتجهيز، ضمن نطاق يحدده احتياج كل مشروع.','Design, construction, renovation and fit-out, shaped around each project’s requirements.');p.search_description=p.summary
        p.body=[self.heading(self.t('خبرات تتصل.\nمن الفكرة إلى العمل المنفذ.','Expertise connected.\nFrom an idea to completed work.'),self.t('تقدم KFATA خدمات التصميم والتنفيذ والمقاولات والتجديد وتنسيق المواقع والتجهيزات والأنظمة التقنية. تضم أعمالها مساحات مصرفية ومكتبية وتجارية وسكنية، ومنشآت تعليمية وصناعية وأعمال طرق وساحات.','KFATA provides design and build, construction, renovation, landscaping, furnishing and technology services. Its portfolio includes banking, office, commercial and residential spaces, educational and industrial facilities, roads and plazas.'),tone='stone'),self.process(),self.listing('service',self.t('تعرّف على مجالات عملنا.','Explore our services.'),list(SERVICES)),self.cta()];self.save(p)
    def update_projects(self):
        for slug,keys in [('anb-new-tower',['anb-workspace-1','anb-workspace-2','anb-tower']),('residential-villas',['residential-interior','residential-courtyard'])]:
            p=self.pages.get(slug)
            if not p or not self.eligible(p):continue
            text=self.t('أعمال تجديد للمساحات المصرفية والمكتبية ضمن البرج، تشمل مساحات العمل الداخلية وتجهيزاتها. تعرض الصور جانبًا من المساحات الواردة في ملف المشروع.','Renovation of banking and office spaces within the tower, including internal workspaces and their fit-out. The images show spaces documented in the project profile.') if slug=='anb-new-tower' else self.t('أعمال إنشاء وتشطيبات لفلل سكنية، تشمل الواجهات والمساحات الداخلية. يبرز العرض تفاصيل التشطيب وعلاقة الفراغات الداخلية بالأفنية والمساحات الخارجية.','Residential villa construction and finishing, including facades and interiors. The presentation shows finishes and the relationship between internal spaces, courtyards and external areas.')
            p.summary=text.split('. ')[0].rstrip('.')+'.';p.search_description=p.summary[:160]
            # Replace only the initial source-selected tower cover, never an
            # independently chosen owner image. Keep the facade in the gallery.
            initial=self.images.get('anb-tower')
            if slug=='anb-new-tower' and initial and p.hero_image_id==initial.pk:
                p.hero_image=self.images['anb-workspace-1']
            p.body=[self.heading(self.t('عن الأعمال','About the work'),text,tone='stone'),('gallery',{'title':self.t('تفاصيل من المشروع','Project details'),'images':[{'image':self.images[k],'caption':self.t('تفاصيل المساحات والتشطيبات','Spaces and finishes')} for k in keys if k in self.images]})];self.save(p)
    def update_sectors(self):
        sectors={
          'banking':('مساحات مصرفية تستجيب لطبيعة الاستخدام.','Banking spaces shaped around their use.','تجديد مبانٍ وفروع مصرفية ومواقع صراف آلي ومراكز تحويل ضمن أعمال الشركة. تختلف احتياجات مناطق الجمهور ومساحات العمل والتجهيزات بحسب طبيعة كل منشأة.','The portfolio includes bank buildings and branches, ATM sites and remittance centres. Public areas, workspaces and fittings depend on the facility and its scope.',['renovation','technology']),
          'commercial':('مساحات للأعمال والاستقبال.','Places for work and welcome.','تشمل الأعمال مساحات مكتبية ومطاعم ومقاهي ومرافق تجارية. يناقَش الإنشاء أو التجديد أو التشطيب والتجهيز وفق حالة الموقع وطبيعة استخدامه.','Work includes offices, restaurants, cafés and commercial facilities. Discuss construction, renovation, finishes and fit-out according to the site and intended use.',['renovation','furnishing']),
          'residential':('من واجهة المبنى إلى تفاصيل المعيشة.','From the facade to the details of living.','تشمل الأعمال إنشاء وتشطيب فلل سكنية وواجهاتها ومساحاتها الداخلية. يبدأ مناقشة النطاق من مرحلة المشروع ومتطلبات المساحات والتشطيبات.','Work includes villa construction and finishing, facades and interiors. Begin with the project stage and requirements for spaces and finishes.',['contracting','furnishing']),
          'education':('منشآت تخدم العملية التعليمية.','Facilities for learning.','يتضمن ملف الأعمال إنشاء وتشطيبات لمبنى مدرسي. حدد مرحلة الموقع والمباني والمرافق المطلوب العمل عليها عند مناقشة منشأة تعليمية.','The portfolio includes school-building construction and finishing. Identify the site stage, buildings and facilities within the proposed scope.',['contracting']),
          'industrial':('تشطيبات للمساحات التشغيلية.','Finishes for operational spaces.','تشمل الأعمال تشطيبات مستودع صناعي. يحدد استخدام المبنى ومتطلبات المساحات التشغيلية والخدمات القائمة نطاق الأعمال المطلوب.','Work includes industrial warehouse finishing. Building use, operational requirements and existing services define the scope.',['contracting','renovation']),
          'public-spaces':('أعمال تربط المباني بمحيطها.','Connecting buildings and their surroundings.','تشمل الأعمال طرقًا وساحات ومعالم معمارية جمالية. يناقَش نطاق الأعمال المدنية والتشطيبات والتنسيق الخارجي بحسب طبيعة الموقع واستخدامه.','Work includes roads, plazas and architectural landmarks. Discuss civil works, finishes and external spaces according to site use.',['contracting','landscaping']),
          'entertainment':('متطلبات مختلفة لتجارب متنوعة.','Different requirements for different experiences.','الترفيه ضمن القطاعات التي تستهدفها خدمات الشركة. شارك طبيعة المرفق واستخدام المساحات وحالة الموقع والأعمال المطلوبة لمناقشة نطاق مناسب.','Entertainment is a listed target sector for the company’s services. Share the facility type, use of space, site stage and required works to discuss the scope.',['design-build','furnishing']),
        }
        for slug,(at,et,a,e,services) in sectors.items():
            p=self.pages.get(slug)
            if not p or not self.eligible(p):continue
            p.summary=self.t(a,e);p.search_description=p.summary[:160]
            p.body=[self.heading(self.t(at,et),self.t(a,e),tone='stone'),self.listing('service',self.t('خدمات يمكن مناقشتها لهذا القطاع','Services to discuss for this sector'),services),self.cta()]
            self.save(p)
    def update_quality(self):
        p=self.pages.get('quality-safety')
        if not p or not self.eligible(p):return
        p.summary=self.t('الاهتمام بجودة التنفيذ ودقة التشطيبات ومتطلبات الموقع ضمن نطاق كل مشروع.','Attention to workmanship, careful finishes and site requirements within each project scope.');p.search_description=p.summary
        p.body=[self.heading(self.t('العناية بالتنفيذ والتفاصيل.','Care in execution and detail.'),self.t('يعبر ملف الشركة عن اهتمام KFATA بجودة التنفيذ والإتقان. تحدد وثائق المشروع نطاق الأعمال ومتطلبات الجودة والسلامة المناسبة للموقع.','The company profile emphasizes quality and workmanship. Project documents define the works and site-specific quality and safety requirements.'),tone='stone'),self.cta()];self.save(p)
    def policies(self,home):
        from home.presentation_policies import policies
        for slug,(title,summary,sections) in policies(self.ar).items():
            p=self.pages.get(slug)
            if p and not self.eligible(p):continue
            if not p:
                p=ContentPage(slug=slug,title=title,locale=home.locale,kind='page')
                other=ContentPage.objects.filter(slug=slug).exclude(locale=home.locale).first()
                if other:p.translation_key=other.translation_key
                home.add_child(instance=p)
            p.summary=summary;p.search_description=summary
            p.body=[self.heading(t,text,tone='stone' if i%2==0 else 'dark') for i,(t,text) in enumerate(sections)];self.save(p)
    def brand(self):
        b=BrandSettings.load()
        defaults={'footer_intro_ar':'تصميم وإنشاء وتجديد وتجهيز للمساحات المصرفية والتجارية والسكنية.','footer_intro_en':'Design, construction, renovation and fit-out for banking, commercial and residential spaces.','footer_cta_ar':'لنبنِ المساحة التي تتصورها.','footer_cta_en':'Let’s build the place you envision.','whatsapp':'966504552257','map_url':'https://www.google.com/maps/search/?api=1&query='+quote(b.address_en or b.address_ar)}
        if not (b.address_en or b.address_ar):defaults.pop('map_url')
        for field,value in defaults.items():
            if not getattr(b,field):setattr(b,field,value)
        if b.font=='tahoma':b.font='plex'
        if not b.footer_columns:
            pages={p.slug:p for p in ContentPage.objects.filter(locale__language_code='ar').live().public()}
            groups=[('الشركة','Company',['about','quality-safety','contact']),('الخدمات','Services',list(SERVICES)),('اكتشف أعمالنا','Explore our work',['projects','banking','commercial','residential','sectors'])]
            b.footer_columns=[('column',{'title_ar':a,'title_en':e,'links':[{'page':pages[s],'label_ar':'','label_en':''} for s in slugs if s in pages]}) for a,e,slugs in groups]
        b.save()
