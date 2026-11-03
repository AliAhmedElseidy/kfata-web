from django.urls import reverse
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.permission_policies import ModelPermissionPolicy
from .models import Enquiry

class SecureAttachmentPanel(FieldPanel):
    def format_value_for_display(self, value):
        return value

class EnquiryPermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, user, action):
        if action == 'add':
            return False
        return super().user_has_permission(user, action)

class EnquiryViewSet(SnippetViewSet):
    model = Enquiry
    icon = 'mail'
    menu_label = 'طلبات العملاء / Enquiries'
    menu_order = 250
    add_to_admin_menu = True
    list_display = ['name', 'company', 'created_at', 'status', 'notification_sent']
    list_filter = ['status', 'notification_sent', 'created_at']
    search_fields = ['name', 'company', 'email', 'phone']
    panels = [FieldPanel(f, read_only=True) for f in ['created_at','language','name','company','email','phone','service','location','message','privacy_version','notification_sent']]
    panels += [SecureAttachmentPanel('secure_attachment', icon='download', heading='المرفق / Attachment', help_text='Private; authorized downloads only.', read_only=True), FieldPanel('status'), FieldPanel('notes')]
    copy_view_enabled = False
    @property
    def permission_policy(self):
        return EnquiryPermissionPolicy(self.model)

def secure_attachment(self):
    if self.attachment:
        return format_html('<a href="{}">تنزيل آمن / Secure download</a>', reverse('private_attachment', args=[self.pk]))
    return '—'

Enquiry.secure_attachment = property(secure_attachment)
register_snippet(EnquiryViewSet)
