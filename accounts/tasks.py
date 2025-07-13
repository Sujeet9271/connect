from celery import shared_task

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from accounts.models import Users

from core.logger import logger

@shared_task(ignore_result=True, queue='accounts')
def send_confirmation_mail(user_id):
    try:
        user = Users.objects.get(id=user_id)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        relativeLink = reverse('accounts:activate_user', kwargs={'uidb64': uidb64, 'token': token})
        baseurl = Site.objects.get_current().domain
        absurl = f"{baseurl}{relativeLink}"
        logger.debug(f'{absurl=}')
        email_body = render_to_string('accounts/activate_user.html', {'activation_url': absurl,'uidb64':uidb64,'token':token,'domain':baseurl,'user':user,'reply_mail':settings.EMAIL_HOST_USER})
        email = EmailMessage(subject='Account Activation' ,body=email_body, from_email=settings.EMAIL_HOST_USER, to=[user.email])
        email.content_subtype = 'html'
        email.send()
        return 'Confirmation Email Sent.'
    except Exception as e:
        logger.exception(str(e))
        return 'Failed to send Confirmation Email.'

    
