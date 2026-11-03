from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse

@hooks.register('register_admin_menu_item')
def enquiries_menu():
    class EnquiriesMenu(MenuItem):
        def is_shown(self, request):
            return request.user.has_perm('home.view_enquiry')
    return EnquiriesMenu('طلبات العملاء / Enquiries', reverse('admin:home_enquiry_changelist'), icon_name='mail', order=250)
