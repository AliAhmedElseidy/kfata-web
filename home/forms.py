from django import forms
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
from .models import Enquiry

class EnquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    consent = forms.BooleanField(label='أوافق على استخدام بياناتي للرد على الطلب / I consent to being contacted about this enquiry')
    class Meta:
        model = Enquiry
        fields = ['name','company','email','phone','service','location','message','attachment']
        labels = {'name':'الاسم / Name','company':'الشركة / Company','email':'البريد / Email','phone':'الهاتف / Phone','service':'الخدمة / Service','location':'الموقع / Location','message':'تفاصيل المشروع / Project details','attachment':'صورة JPEG أو PNG، حتى 5MB / JPEG or PNG, up to 5MB'}
        widgets = {'message': forms.Textarea(attrs={'rows':5})}
    def clean_website(self):
        if self.cleaned_data['website']:
            raise ValidationError('Unable to submit.')
        return ''
    def clean_attachment(self):
        f = self.cleaned_data.get('attachment')
        if not f: return f
        if f.size > 5 * 1024 * 1024:
            raise ValidationError('Maximum file size is 5MB.')
        ext = f.name.rsplit('.',1)[-1].lower()
        if ext not in {'pdf','jpg','jpeg','png'}:
            raise ValidationError('Only PDF, JPEG and PNG files are accepted.')
        if ext == 'pdf':
            # Public PDF upload is disabled until a sanitizer/scanner is configured.
            raise ValidationError('For now, please attach a JPEG or PNG image; request a secure channel for PDF plans.')
        try:
            im = Image.open(f)
            if im.format not in {'JPEG','PNG'} or (ext=='png') != (im.format=='PNG'):
                raise ValueError('Image format does not match its extension.')
            im.verify()
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise ValidationError('Invalid image.')
        finally:
            f.seek(0)
        # Re-encode to discard metadata and any appended payload.
        from django.core.files.uploadedfile import SimpleUploadedFile
        from io import BytesIO
        im = Image.open(f)
        im.thumbnail((4096,4096))
        data = BytesIO()
        im.convert('RGB').save(data, format='JPEG', quality=90)
        return SimpleUploadedFile('attachment.jpg', data.getvalue(), content_type='image/jpeg')
