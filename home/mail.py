"""Owner-configured SMTP. Secrets are encrypted in storage and never logged."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.views.decorators.debug import sensitive_variables
from cryptography.fernet import Fernet


@sensitive_variables()
def _cipher():
    key=settings.SMTP_ENCRYPTION_KEY
    if not key: raise ImproperlyConfigured('SMTP encryption key is unavailable.')
    return Fernet(key)


@sensitive_variables()
def encrypt_secret(password):
    return _cipher().encrypt(password.encode()).decode()


@sensitive_variables()
def decrypt_secret(token):
    return _cipher().decrypt(token.encode()).decode() if token else ''


def notification_route():
    if settings.OUTBOUND_EMAIL_DISABLED: return None
    from .models import SMTPSettings
    config=SMTPSettings.load()
    if config.delivery_mode=='panel': return config.sender,config.recipient
    if config.delivery_mode=='environment' and settings.EMAIL_HOST and settings.ENQUIRY_EMAIL:
        return settings.DEFAULT_FROM_EMAIL,settings.ENQUIRY_EMAIL
    return None


class ConfiguredSMTPBackend(BaseEmailBackend):
    @sensitive_variables()
    def send_messages(self,email_messages):
        if not email_messages or settings.OUTBOUND_EMAIL_DISABLED: return 0
        from .models import SMTPSettings
        config=SMTPSettings.load()
        if config.delivery_mode=='off': return 0
        if config.delivery_mode=='panel':
            if not config.host: raise ImproperlyConfigured('SMTP host is not configured.')
            for message in email_messages: message.from_email=config.sender
            options=dict(host=config.host,port=config.port,username=config.username,password=decrypt_secret(config.password_ciphertext),use_tls=config.transport=='starttls',use_ssl=config.transport=='ssl',timeout=8)
        else:
            if not settings.EMAIL_HOST: return 0
            options=dict(host=settings.EMAIL_HOST,port=settings.EMAIL_PORT,username=settings.EMAIL_HOST_USER,password=settings.EMAIL_HOST_PASSWORD,use_tls=settings.EMAIL_USE_TLS,use_ssl=getattr(settings,'EMAIL_USE_SSL',False),timeout=settings.EMAIL_TIMEOUT)
        connection=SMTPBackend(fail_silently=self.fail_silently,**options)
        return connection.send_messages(email_messages)
