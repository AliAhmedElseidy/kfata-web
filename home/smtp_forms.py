from django import forms
from django.views.decorators.debug import sensitive_variables
from wagtail.admin.forms import WagtailAdminModelForm
from .models import SMTPSettings


class SMTPSettingsForm(WagtailAdminModelForm):
    smtp_password = forms.CharField(required=False,max_length=1024,strip=False,label='كلمة المرور الجديدة / New password',widget=forms.PasswordInput(render_value=False,attrs={'autocomplete':'new-password'}),help_text='Leave blank to keep the stored password. The current value is never returned to the browser.')
    clear_password = forms.BooleanField(required=False,label='حذف كلمة المرور المحفوظة / Clear stored password')
    password_saved = forms.BooleanField(required=False,disabled=True,label='توجد كلمة مرور محفوظة / Password is stored')
    class Meta:
        model=SMTPSettings
        fields=['delivery_mode','host','port','transport','username','sender','recipient']
        widgets={'username':forms.TextInput(attrs={'autocomplete':'off'})}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['password_saved'].initial=bool(self.instance.password_ciphertext)

    @sensitive_variables()
    def clean(self):
        data=super().clean()
        password=data.get('smtp_password','')
        clear=data.get('clear_password',False)
        self._new_ciphertext=None
        if clear and password: raise forms.ValidationError('Choose either a new password or clearing the stored password.')
        if password:
            from .mail import encrypt_secret
            try: self._new_ciphertext=encrypt_secret(password)
            except Exception: raise forms.ValidationError('The SMTP encryption key is unavailable; contact the administrator.') from None
        if data.get('delivery_mode')=='panel':
            for field in ['host','sender','recipient']:
                if not data.get(field): self.add_error(field,'Required for control-panel delivery.')
            if clear and data.get('username'): self.add_error('clear_password','Disable delivery before clearing the password.')
            if data.get('username') and not password and not self.instance.password_ciphertext:
                self.add_error('smtp_password','Enter the SMTP account password.')
            if data.get('username') and not password and not clear and self.instance.password_ciphertext:
                from .mail import decrypt_secret
                try: decrypt_secret(self.instance.password_ciphertext)
                except Exception: self.add_error('smtp_password','Re-enter the password; the stored credential cannot be opened.')
        return data

    @sensitive_variables()
    def save(self,commit=True):
        instance=super().save(commit=False)
        if self.cleaned_data.get('clear_password'): instance.password_ciphertext=''
        elif self._new_ciphertext is not None: instance.password_ciphertext=self._new_ciphertext
        if commit:
            instance.save();self.save_m2m()
        return instance
