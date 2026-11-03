"""Apply the company-contact/retention decisions explicitly approved on 2026-11-03."""
from html import escape
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from home.models import BrandSettings, ContentPage


class Command(BaseCommand):
    help = 'Configure approved contacts and privacy. Explicit --enable-enquiries activates the form.'

    def add_arguments(self, parser):
        parser.add_argument('--hosting-country',required=True)
        parser.add_argument('--enable-enquiries',action='store_true')

    @transaction.atomic
    def handle(self, **options):
        country=options['hosting_country'].strip()
        if not country: raise CommandError('Owner-confirmed hosting country is required.')
        brand=BrandSettings.load()
        approved={'email':'info@kfata.com','phone':'+966112337351','secondary_phone':'+966504552257','address_ar':'8508 فرع طريق الملك فهد، 3817، حي العليا، الرياض، المملكة العربية السعودية','address_en':'8508 King Fahad Branch, 3817, Al Olaya, Riyadh, Saudi Arabia'}
        for field,value in approved.items():
            if not getattr(brand,field): setattr(brand,field,value)
        if settings.ENQUIRY_RETENTION_DAYS != 90:
            raise CommandError('Review privacy copy before changing the approved 90-day retention.')
        for lang in ['ar','en']:
            page=ContentPage.objects.filter(slug='privacy',locale__language_code=lang).first()
            if not page: raise CommandError('Run seed_content first.')
            latest=page.get_latest_revision()
            if latest and latest.user_id:
                if not page.live: raise CommandError('Editor-owned privacy draft must be reviewed/published from Wagtail.')
                continue
            arabic=lang=='ar'
            sections=self.copy(arabic,country,brand)
            page.summary='كيف نعالج بيانات التواصل وطلبات عروض الأسعار.' if arabic else 'How we process contact details and quotation enquiries.'
            page.search_description=page.summary
            page.body=[('heading',{'eyebrow':'KFATA','title':title,'text':'<p>'+escape(text)+'</p>'}) for title,text in sections]
            page.save_revision().publish()
        if options['enable_enquiries']: brand.enquiries_enabled=True
        brand.save()
        self.stdout.write(self.style.SUCCESS('Approved contacts and bilingual privacy configured. Enquiry collection: '+str(brand.enquiries_enabled)))

    def copy(self, ar, country, brand):
        if country.lower() in {'saudi arabia','sa','السعودية','المملكة العربية السعودية'}:
            country='المملكة العربية السعودية' if ar else 'Saudi Arabia'
        if ar:
            return [
                ('الجهة المسؤولة والتواصل',f'تدير KFATA هذا الموقع. للتواصل بشأن بياناتك: {brand.email}، هاتف {brand.phone}. العنوان: {brand.address_ar}. نسخة السياسة {brand.privacy_version}.'),
                ('البيانات والغرض', 'يطلب نموذج عرض السعر الاسم والبريد والهاتف وتفاصيل المشروع، ويمكن إضافة الشركة والخدمة والموقع وصورة اختيارية. نستخدمها لتقييم الطلب والرد والتواصل بشأن المشروع، بناءً على موافقتك عند الإرسال. يمكنك التواصل مباشرة بالبريد أو الهاتف بدل النموذج. لا ترفق هويات أو معلومات غير لازمة للطلب.'),
                ('التخزين والمرفقات والوصول',f'الاستضافة الرئيسية للموقع في {country} وفق بيانات الاستضافة التي اعتمدتها إدارة الشركة. تنتقل البيانات إلى الموقع عبر HTTPS وتُحفظ في قاعدة بيانات ومجلد مرفقات خاص غير منشور. يصل إليها المستخدمون المخولون من الشركة والدعم الفني حسب الحاجة. يقبل النموذج صور JPEG وPNG حتى 5 ميجابايت، مع إعادة ترميزها لإزالة البيانات الوصفية؛ لا يقبل PDF حاليًا.'),
                ('مدة الاحتفاظ والحذف','تحذف طلبات النموذج ومرفقاتها بعد 90 يومًا من الإرسال في دورة الحذف اليومية التالية. لا تُستخدم قاعدة هذا النموذج لأرشفة العقود. قد تُنقل المعلومات اللازمة لعلاقة تعاقدية إلى أنظمة الشركة لأغراض التعاقد وفق إشعاراتها الخاصة. تحتفظ النسخ الاحتياطية اليومية بنسخ استعادة لمدة 14 يومًا، وقد تبقى بيانات حُذفت من النظام داخل نسخة سابقة إلى انتهاء دورتها. نسخ الاستعادة مقيدة الوصول وليست للاستخدام اليومي.'),
                ('البريد والمشاركة','في الإعداد الحالي لا يرسل الموقع بريدًا تلقائيًا؛ يراجع الفريق الطلبات من لوحة الإدارة. لا تُرسل تفاصيل الطلبات إلى منصات إعلانية أو أدوات تحليل أو خدمات ذكاء اصطناعي. عند إعداد إشعار بريدي لاحقًا، يحمل الإشعار رقم الطلب ورابط الإدارة دون محتوى الطلب أو مرفقاته؛ تبقى مراسلات الرد التي تجريها الشركة عبر البريد أو الهاتف ضمن التعامل المباشر معها.'),
                ('ملفات الارتباط والسجلات','نستخدم ملفات ارتباط وظيفية لحماية النماذج والجلسات والدخول الإداري، ولا توجد أدوات تتبع إعلاني أو تحليلات زوار. تسجل خدمة الويب عنوان IP والمسار المطلوب ووقت الطلب وبيانات المتصفح لأغراض التشغيل والأمان، مع تدوير يومي و14 نسخة سجلات مؤرشفة إضافة للسجل الجاري. يُستخدم مفتاح مشتق من عنوان IP للحد من الإرسال الآلي خلال نافذة عمل تبلغ 10 دقائق؛ لا يُضاف عنوان IP إلى سجل طلب عرض السعر.'),
                ('طلبات الخصوصية',f'يمكن طلب الاطلاع على بياناتك المرسلة أو تصحيحها أو حذفها أو سحب الموافقة بالتواصل على {brand.email}. نتحقق من هوية صاحب الطلب بالقدر اللازم ونراجعه وفق المتطلبات النظامية ذات الصلة، دون طلب وثائق هوية عبر هذا النموذج. حدّث بيانات التواصل إذا احتجت متابعة طلبك. لا يستخدم هذا الموقع قرارات آلية لتقييم أهلية الأشخاص.'),
            ]
        return [
            ('Controller and contact',f'KFATA operates this website. Contact {brand.email} or {brand.phone} about your data. Address: {brand.address_en}. Policy version {brand.privacy_version}.'),
            ('Data and purpose','The quotation form asks for your name, email, telephone and project details. Company, service, location and one image are optional. We use these details to assess and respond to your project enquiry, with your consent when submitting. You may contact us by email or telephone instead. Do not attach identity documents or information unrelated to the enquiry.'),
            ('Storage, attachments and access',f'The primary website hosting location is {country}, as confirmed by company management. Data reaches the website over HTTPS and is stored in its database and a private, unpublished attachment directory. Authorized company staff and necessary technical support can access it. The form accepts JPEG/PNG images up to 5MB and re-encodes them to remove metadata. PDF upload is currently unavailable.'),
            ('Retention and deletion','Form enquiries and attachments are deleted after 90 days in the next daily deletion cycle. This form database is not a contract archive. Information needed for a contractual relationship may be transferred to company systems for that purpose under their own notices. Daily recovery backups retain snapshots for 14 days; deleted live data may remain in an earlier snapshot until that cycle ends. Recovery copies have restricted access and are not used for routine processing.'),
            ('Email and sharing','The website currently sends no automatic email; staff review enquiries in the administration panel. It does not transmit enquiry details to advertising, analytics or AI services. If email notifications are configured later, they contain an enquiry reference and administration link, without enquiry text or attachments. Any subsequent email or telephone correspondence is handled directly by the company.'),
            ('Functional cookies and logs','Functional cookies support form security, sessions and administration sign-in. No visitor analytics or advertising trackers are installed. Web logs include the IP address, requested path, time and browser information for operations/security, with daily rotation and 14 archived log copies plus the current log. A key derived from the IP address limits automated submissions over a ten-minute window; IP addresses are not added to the quotation record.'),
            ('Privacy requests',f'Contact {brand.email} to request access, correction, deletion or withdrawal of consent for the data you submitted. We verify requests as necessary and review them under applicable requirements; do not upload identity documents to this form. Update your contact information when needed for a response. This website does not make automated decisions about personal eligibility.'),
        ]
