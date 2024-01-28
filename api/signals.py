from datetime import datetime

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import ApplicationCompensation


@receiver(post_save, sender=ApplicationCompensation)
def send_status_email(sender, instance, created, **kwargs):
    if instance.status in [ApplicationCompensation.Status.APPROVED, ApplicationCompensation.Status.NOT_APPROVED] and not created:

        subject = "Application Status Update"
        message = render_to_string('email_template.html', {
            'username': instance.user.first_name,
            'policy_number': instance.policy_number,
            'status': instance.status,
            'current_year': datetime.now().year
        })
        recipient_list = [instance.user.email]

        send_mail(subject, message, None, recipient_list, html_message=message)
