from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def no_action(report):
    subject = "AR Project Moderation Update: No Action Taken"
    message = render_to_string('moderation/no_action_email.html', {
        'report': report,
        'site_name': settings.SITE_NAME,
        'domain': settings.SITE_DOMAIN,
        'message_to_reporter': report.message_to_reporter,
        'message_to_user': report.message_to_user,
    })
    email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [report.reporter.email, report.ar_object.creator.email])
    email.send()



def warn_user(user, report):
    subject = 'AR Project Warning: Inappropriate Content Reported'
    message = render_to_string('moderation/warn_user_email.html', {
        'user': user,
        'report': report,
        'site_name': settings.SITE_NAME,
        'domain': settings.SITE_DOMAIN,
        'message_to_user': report.message_to_user,
    })
    email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.send()

    subject_reporter = 'AR PRoject Moderation Update: User Warned'
    message_reporter = render_to_string('moderation/warn_user_reporter_email.html',
        {
            'report': report,
            'site_name': settings.SITE_NAME,
            'domain': settings.SITE_DOMAIN,
            'message_to_reporter': report.message_to_reporter,
        })
    email_reporter = EmailMultiAlternatives(subject_reporter, message_reporter, settings.DEFAULT_FROM_EMAIL, [report.reporter.email])
    email_reporter.send()


def remove_object(report):
    ar_object = report.ar_object
    ar_object.is_active = False
    ar_object.save()
    
    subject = 'AR Project Object Removed: Inappropriate Content Reported'
    message = render_to_string('moderation/remove_object_email.html', {
        'ar_object': ar_object,
        'report': report,
        'site_name': settings.SITE_NAME,
        'domain': settings.SITE_DOMAIN,
        'message_to_user': report.message_to_user,
    })
    email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [ar_object.creator.email])
    email.send()

    subject_reporter = 'AR Project Moderation Update: Object Removed'
    message_reporter = render_to_string('moderation/remove_object_reporter_email.html',
        {
            'report': report,
            'site_name': settings.SITE_NAME,
            'domain': settings.SITE_DOMAIN,
            'message_to_reporter': report.message_to_reporter,
        })
    email_reporter = EmailMultiAlternatives(subject_reporter, message_reporter, settings.DEFAULT_FROM_EMAIL, [report.reporter.email])
    email_reporter.send()


def ban_user(user, report, ban_expiration):
    user.account_status = "Suspended"
    user.ban_expiration = ban_expiration
    user.save()
    
    subject = 'AR Project Account Banned: Inappropriate Content Reported'
    message = render_to_string('moderation/ban_user_email.html', {
        'user': user,
        'report': report,
        'site_name': settings.SITE_NAME,
        'domain': settings.SITE_DOMAIN,
        'message_to_user': report.message_to_user,
    })
    email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.send()

    subject_reporter = 'AR Project Moderation Update: User Banned'
    message_reporter = render_to_string('moderation/ban_user_reporter_email.html',
        {
            'report': report,
            'site_name': settings.SITE_NAME,
            'domain': settings.SITE_DOMAIN,
            'message_to_reporter': report.message_to_reporter,
            'ban_expiration': user.ban_expiration,
        })
    email_reporter = EmailMultiAlternatives(subject_reporter, message_reporter, settings.DEFAULT_FROM_EMAIL, [report.reporter.email])
    email_reporter.send()