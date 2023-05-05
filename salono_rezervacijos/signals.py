from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profilis, PaslaugosRezervacija
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profilis.objects.create(user=instance)
    else:
        instance.profilis.save()
    print('printas is signals gavejo, kwargs', kwargs)


@receiver(post_save, sender=PaslaugosRezervacija)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Rezervacijos patvirtinimas'
        html_message = render_to_string('patvirtinimas.html', {'paslaugos_rezervacija': instance})
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.klientas.email],
            fail_silently=False,
            html_message=html_message,
        )