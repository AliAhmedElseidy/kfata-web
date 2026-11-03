from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name','company','created_at','status','notification_sent']
    list_filter = ['status','notification_sent','created_at']
    search_fields = ['name','company','email','phone']
    readonly_fields = ['created_at','language','name','company','email','phone','service','location','message','download_attachment','notification_sent']
    fields = readonly_fields + ['status','notes']
    def download_attachment(self, obj):
        if obj.attachment:
            return format_html('<a href="{}">تنزيل آمن / Secure download</a>', reverse('private_attachment', args=[obj.pk]))
        return '—'
    def has_add_permission(self, request): return False
