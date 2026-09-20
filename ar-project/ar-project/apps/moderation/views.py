
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import random, requests, resend, os, pytz
from datetime import datetime, timedelta

from ar_project.utils import set_base_template

from .models import TextObjectReport
from .forms import TextObjectReportForm, BanUserForm, UnbanUserForm
from .utils import no_action, warn_user, remove_object, ban_user

from apps.users.models import CustomUser
from apps.objects.models import ARTextObject


def report_object(request, object_id, object_type):
    if object_type == 'Text':
        reported_object = get_object_or_404(ARTextObject, id=object_id)

    if request.method == 'POST':
        form = ObjectReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.ar_object = object
            report.reporter = request.user
            report = form.save(commit=False)
            note = f"{timezone.now()}: Object reported by {request.user.username}."
            report.system_notes.append(note)

            note = f"{timezone.now()}: Object reported by {request.user.username} for {report.reason}."
            reported_object.system_notes.append(note)
            reported_object.save()
            messages.success(request, 'Object reported successfully.')
            return redirect('object_detail', object_id=object.id)
        else:
            messages.error(request, f'There was an error with the form: {form.errors}. Please correct it and try again.')
    else:
        form = ObjectReportForm()

    return render(request, 'objects/report_object.html', {'form': form, 'object': reported_object})


@login_required()
def view_reports(request):
    if not request.user.user_type == 'Admin':
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('home')

    reports = ObjectReport.objects.filter(reviewed=False).order_by('-reported_at')
    return render(request, 'objects/view_reports.html', {'reports': reports})


@login_required()
def review_report(request, report_id):
    if not request.user.user_type == 'Admin':
        messages.error(request, 'You do not have permission to review reports.')
        return redirect('home')

    report = ObjectReport.objects.get_or_404(id=report_id)

    if request.method == 'POST':
        action_taken = request.POST.get('action_taken', '')
        report.mark_reviewed(action_taken)
        note = f"{timezone.now()}: Report reviewed by {request.user.username}. Action taken: {action_taken}"
        report.system_notes.append(note)
        report.save()

        object_note = f"{timezone.now()}: Report reviewed by {request.user.username}. Action taken: {action_taken}"
        report.ar_object.system_notes.append(object_note)
        report.ar_object.save()

        messages.success(request, 'Report reviewed successfully.')
        return redirect('view_reports')

    return render(request, 'objects/review_report.html', {'report': report})


@login_required()
def action_report(request, report_id):
    if not request.user.user_type == 'Admin':
        messages.error(request, 'You do not have permission to take action on reports.')
        return redirect('home')

    report = ObjectReport.objects.get_or_404(id=report_id)
    if request.method == 'POST':
        form = ObjectReviewForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)

            if report.action_taken == 'No Action':
                note = f"{timezone.now()}: {request.user.username} decided to take no action on the report."
                no_action(report)
            elif report.action_taken == 'Warn User':
                note = f"{timezone.now()}: {request.user.username} warned the object creator."
                warn_user(report.ar_object.creator, report)
            elif report.action_taken == 'Remove Object':
                note = f"{timezone.now()}: {request.user.username} removed the reported object."
                remove_object(report)
            elif report.action_taken == 'Ban User':
                note = f"{timezone.now()}: {request.user.username} banned the object creator."
                ban_user(report.ar_object.creator, form.ban_expiration)
            report.system_notes.append(note)
            report.object.system_notes.append(note)

            report.mark_reviewed(report.action_taken)
            note = f"{timezone.now()}: Action taken by {request.user.username}. Action: {report.action_taken}"
            report.system_notes.append(note)
            report.save()


            object_note = f"{timezone.now()}: Action taken by {request.user.username}. Action: {report.action_taken}"
            report.ar_object.system_notes.append(object_note)
            report.ar_object.save()

            messages.success(request, 'Action taken on report successfully.')
            return redirect('view_reports')
        else:
            messages.error(request, f'There was an error with the form: {form.errors}. Please correct it and try again.')
    else:
        form = ObjectReviewForm(instance=report)


@login_required()
def ban_user_view(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    form = BanUserForm()

    if request.method == 'POST':
        form = BanUserForm(request.POST)
        if form.is_valid():
            ban_expiration = form.cleaned_data['ban_expiration']
            ban_reason = form.cleaned_data['ban_reason']
            message_to_user = form.cleaned_data['message_to_user']

            user.account_status = 'Banned'
            user.ban_expiration = ban_expiration
            user.save()

            note = f"{timezone.now()}: User banned by admin until {ban_expiration}. Reason: {ban_reason}"
            user.system_notes.append(note)
            user.save()

            subject = 'AR Project Account Banned'
            message = render_to_string('moderation/ban_user_email.html', {
                'user': user,
                'ban_expiration': ban_expiration,
                'ban_reason': ban_reason,
                'site_name': settings.SITE_NAME,
                'domain': settings.SITE_DOMAIN,
                'message_to_user': message_to_user,
            })
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.send()

            messages.success(request, f'User {user.username} has been banned successfully.')
            return redirect('view_reports')
        else:
            messages.error(request, f'There was an error with the form: {form.errors}. Please correct it and try again.')
    return render(request, 'moderation/ban_user.html', {'form': form, 'user': user})


@login_required()
def unban_user_view(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    form = UnbanUserForm()

    if request.method == 'POST':
        form = UnbanUserForm(request.POST)
        if form.is_valid():
            message_to_user = form.cleaned_data['message_to_user']

            user.account_status = 'Active'
            user.ban_expiration = None
            user.save()

            note = f"{timezone.now()}: User unbanned by admin."
            user.system_notes.append(note)
            user.save()

            subject = 'AR Project Account Unbanned'
            message = render_to_string('moderation/unban_user_email.html', {
                'user': user,
                'site_name': settings.SITE_NAME,
                'domain': settings.SITE_DOMAIN,
                'message_to_user': message_to_user,
            })
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.send()

            messages.success(request, f'User {user.username} has been unbanned successfully.')
            return redirect('view_reports')
        else:
            messages.error(request, f'There was an error with the form: {form.errors}. Please correct it and try again.')

    return render(request, 'moderation/unban_user.html', {'form': form, 'user': user})


