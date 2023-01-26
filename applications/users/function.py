"""Funciones extras de python para la aplicacion users."""
import random
import string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template
from django import forms
from fortuna_303.settings.base import get_secret

def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def notification_admin_by_mail(affair: str, message: str):
    # Enviamos un correo de notificación de un evento
    email_remitente = get_secret("EMAIL")
    send_mail(affair, message, email_remitente, [email_remitente,])


def create_mail(user_mail, subject, template_name, context):
    template = get_template(template_name)
    content = template.render(context)

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=get_secret("EMAIL"),
        to=[
            user_mail
        ],
        cc=[]
    )

    message.attach_alternative(content, 'text/html')
    return message
