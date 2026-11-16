from django import forms
from wagtail_2fa.forms import TokenForm
from wagtail_2fa.views import LoginView


class DeviceTokenForm(TokenForm):
    # django-otp 1.7 requires the user to select a confirmed device explicitly.
    otp_device = forms.ChoiceField(label="Authenticator device / جهاز المصادقة")

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["otp_device"].choices = self.device_choices(user)
        self.extra_fields = [("otp_device", self["otp_device"])]


class DeviceLoginView(LoginView):
    form_class = DeviceTokenForm
