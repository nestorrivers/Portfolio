

import django.contrib.messages as messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from ..models import ARTextObjectTemplate, TextObjectInteraction, ARTextObject
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone


from ar_project.utils import set_base_template

from apps.channels.models import ARChannel
from apps.notifications.models import Notification

from ..models import ARTextObject, TextObjectInteraction
from ..forms import ARTextObjectTemplateForm, ARTextObjectForm, SuspendObjectForm



@login_required
def create_ar_text_template(request):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to create AR Text Object Templates.')
        return redirect('home')

    if request.method == 'POST':
        form = ARTextObjectTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            ar_text_object_template = form.save(commit=False)
            ar_text_object_template.creator = request.user
            ar_text_object_template.save()
            form.save_m2m()
            messages.success(request, 'AR Text Object Template created successfully.')
            return redirect('ar_text_object_template_detail', pk=ar_text_object_template.pk)
    else:
        form = ARTextObjectTemplateForm()
    
    context = {
        'form': form,
    }
    set_base_template(request)
    return render(request, 'objects/create_ar_text_object_template.html', context)


@login_required
def view_ar_text_template_details(request, pk):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to view AR Text Object Templates.')
        return redirect('home')

    ar_text_object_template = get_object_or_404(ARTextObjectTemplate, pk=pk)

    context = {
        'ar_text_object_template': ar_text_object_template,
    }
    set_base_template(request)
    return render(request, 'objects/view_ar_text_object_template.html', context)


@login_required
def edit_ar_text_template(request, pk):
    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to edit AR Text Object Templates.')
        return redirect('home')

    ar_text_object_template = get_object_or_404(ARTextObjectTemplate, pk=pk)

    if request.method == 'POST':
        form = ARTextObjectTemplateForm(request.POST, request.FILES, instance=ar_text_object_template)
        if form.is_valid():
            form.save()
            messages.success(request, 'AR Text Object Template updated successfully.')
            return redirect('ar_text_object_template_detail', pk=ar_text_object_template.pk)
    else:
        form = ARTextObjectTemplateForm(instance=ar_text_object_template)
    
    context = {
        'form': form,
        'ar_text_object_template': ar_text_object_template,
    }
    set_base_template(request)
    return render(request, 'objects/edit_ar_text_object_template.html', context)


@login_required
def delete_ar_text_template(request, pk):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to delete AR Text Object Templates.')
        return redirect('home')

    ar_text_object_template = get_object_or_404(ARTextObjectTemplate, pk=pk)

    if request.method == 'POST':
        ar_text_object_template.delete()
        messages.success(request, 'AR Text Object Template deleted successfully.')
        return redirect('admin_dashboard')
    
    context = {
        'ar_text_object_template': ar_text_object_template,
    }
    set_base_template(request)
    return render(request, 'objects/delete_ar_text_object_template.html', context)


@login_required
def ar_text_template_list(request):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to view AR Text Object Templates.')
        return redirect('home')

    ar_text_object_templates = ARTextObjectTemplate.objects.all()

    context = {
        'ar_text_object_templates': ar_text_object_templates,
    }
    set_base_template(request)
    return render(request, 'objects/ar_text_object_template_list.html', context)


