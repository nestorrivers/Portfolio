

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
def create_ar_text_object(request):

    if request.method == 'POST':
        print('hello')
        form = ARTextObjectForm(request.POST, request.FILES)
        if form.is_valid():
            ar_text_object = form.save(commit=False)
            ar_text_object.creator = request.user
            ar_text_object.save_and_moderate()
            form.save_m2m()
            messages.success(request, 'AR Text Object created successfully.')
            return redirect('view_ar_text_object_details', pk=ar_text_object.pk)
        else:
            print(form.errors)

    else:
        form = ARTextObjectForm()
    
    context = {
        'form': form,
        'base_template': set_base_template(request),
    }
    
    return render(request, 'objects/text-object-form.html', context)


@login_required
def create_ar_text_object_channel_specific(request, channel_slug):

    if request.method == 'POST':
        channel = ARChannel.objects.get(slug=channel_slug)
        form = ARTextObjectForm(request.POST, request.FILES)
        if form.is_valid():
            ar_text_object = form.save(commit=False)
            ar_text_object.creator = request.user
            ar_text_object.channel = channel
            ar_text_object.save_and_moderate()
            form.save_m2m()
            messages.success(request, 'AR Text Object created successfully.')
            return redirect('view_ar_text_object_details', pk=ar_text_object.pk)
        else:
            print(form.errors)

    else:
        form = ARTextObjectForm()
    
    context = {
        'form': form,
        'base_template': set_base_template(request),
    }
    
    return render(request, 'objects/text-object-form.html', context)



@login_required
def view_ar_text_object_details(request, pk):


    user = request.user

    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    if ar_text_object.creator != user and user.user_type not in ['Admin']:
        messages.error(request, 'You do not have permission to view this AR Text Object.')
        return redirect('home')

    object_interaction, created = TextObjectInteraction.objects.get_or_create(user=user, text_object=ar_text_object)

    print(object_interaction)


    context = {
        'ar_text_object': ar_text_object,
        'base_template': set_base_template(request),
        'object_interaction': object_interaction,
    }
    return render(request, 'objects/view-text-object.html', context)


@login_required
def edit_ar_text_object(request, pk):


    user = request.user

    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    if ar_text_object.creator != user:
        messages.error(request, 'You do not have permission to edit this AR Text Object.')
        return redirect('home')


    if request.method == 'POST':
        form = ARTextObjectForm(request.POST, request.FILES, instance=ar_text_object)
        if form.is_valid():
            form.save_and_moderate()
            messages.success(request, 'AR Text Object updated successfully.')
            return redirect('ar_text_object_detail', pk=ar_text_object.pk)
    else:
        form = ARTextObjectForm(instance=ar_text_object)
    
    context = {
        'form': form,
        'ar_text_object': ar_text_object,
        'base_template': set_base_template(request),
    }
    return render(request, 'objects/text-object-form.html', context)


@login_required
def delete_ar_text_object(request, pk):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to delete AR Text Objects.')
        return redirect('home')

    user = request.user

    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    if ar_text_object.creator != user:
        messages.error(request, 'You do not have permission to delete this AR Text Object.')
        return redirect('home')

    if request.method == 'POST':
        ar_text_object.delete()
        messages.success(request, 'AR Text Object deleted successfully.')
        return redirect('user_dashboard')
    
    context = {
        'ar_text_object': ar_text_object,
    }
    set_base_template(request)
    return render(request, 'objects/delete_ar_text_object.html', context)


@login_required
def suspend_ar_text_object(request, pk):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to suspend AR Text Objects.')
        return redirect('home')

    ar_text_object = get_object_or_404(ARTextObject, pk=pk)

    if request.method == 'POST':
        ar_text_object.visibility = 'Suspended'
        ar_text_object.save()
        messages.success(request, 'AR Text Object suspended successfully.')
        return redirect('ar_text_object_detail', pk=ar_text_object.pk)
    
    context = {
        'ar_text_object': ar_text_object,
    }
    set_base_template(request)
    return render(request, 'objects/suspend_ar_text_object.html', context)


@login_required
def like_ar_text_object(request, pk):

    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'You must be logged in to like objects.')
        return redirect('login')
    
    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    interaction, created = TextObjectInteraction.objects.get_or_create(
        user=user,
        text_object=ar_text_object
    )
    interaction.liked = True
    interaction.save()
    messages.success(request, 'You liked the AR Text Object.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    
    return redirect('view_ar_text_object_details', pk=ar_text_object.pk)


@login_required
def unlike_ar_text_object(request, pk):

    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'You must be logged in to unlike objects.')
        return redirect('login')
    
    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    interaction = TextObjectInteraction.objects.filter(
        user=user,
        text_object=ar_text_object,
        liked=True
    ).first()
    if interaction:
        interaction.liked = False
        interaction.save()
        messages.success(request, 'You unliked the AR Text Object.')
    else:
        messages.error(request, 'You have not liked this AR Text Object.')
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('ar_text_object_detail', pk=ar_text_object.pk)


@login_required
def hide_ar_text_object(request, pk):

    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'You must be logged in to hide objects.')
        return redirect('login')
    
    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    interaction, created = TextObjectInteraction.objects.get_or_create(
        user=user,
        text_object=ar_text_object
    )
    interaction.hidden = True
    interaction.save()
    messages.success(request, 'You hid the AR Text Object.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('ar_text_object_detail', pk=ar_text_object.pk)


@login_required
def unhide_ar_text_object(request, pk):

    user = request.user
    if not user.is_authenticated:
        messages.error(request, 'You must be logged in to unhide objects.')
        return redirect('login')
    
    ar_text_object = get_object_or_404(ARTextObject, pk=pk)
    interaction = TextObjectInteraction.objects.filter(
        user=user,
        text_object=ar_text_object
    ).first()
    if interaction:
        interaction.hidden = False
        interaction.save()
        messages.success(request, 'You unhid the AR Text Object.')
    else:
        messages.error(request, 'This AR Text Object is not hidden.')
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('ar_text_object_detail', pk=ar_text_object.pk)



@login_required
def ar_text_object_list_admin(request):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to view AR Text Objects.')
        return redirect('home')

    user = request.user

    ar_text_objects = ARTextObject.objects.filter(creator=user)

    context = {
        'ar_text_objects': ar_text_objects,
        'base_template': set_base_template(request),
    }
    return render(request, 'objects/objects-list-admin.html', context)


@login_required
def ar_text_object_list_user(request):

    user = request.user

    # Get filter and search parameters
    search_query = request.GET.get('search', '')
    visibility_filter = request.GET.get('visibility', '')
    template_filter = request.GET.get('template', '')
    sort_by = request.GET.get('sort', '-created_at')

    # Start with user's objects
    ar_text_objects = ARTextObject.objects.filter(creator=user)

    # Apply search
    if search_query:
        ar_text_objects = ar_text_objects.filter(
            Q(text__icontains=search_query) |
            Q(title__icontains=search_query)
        )

    # Apply visibility filter
    if visibility_filter:
        ar_text_objects = ar_text_objects.filter(visibility=visibility_filter)

    # Apply template filter
    if template_filter:
        ar_text_objects = ar_text_objects.filter(template_id=template_filter)

    # Apply sorting
    ar_text_objects = ar_text_objects.order_by(sort_by)

    # Pagination
    paginator = Paginator(ar_text_objects, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all templates for filter dropdown
    templates = ARTextObjectTemplate.objects.all()

    context = {
        'ar_text_objects': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'visibility_filter': visibility_filter,
        'template_filter': template_filter,
        'sort_by': sort_by,
        'templates': templates,
        'base_template': set_base_template(request),
    }
    return render(request, 'objects/objects-list-user.html', context)


@login_required
def suspend_ar_text_object(request, pk):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to suspend AR Text Objects.')
        return redirect('home')


    ar_text_object = get_object_or_404(ARTextObject, pk=pk)

    suspend_form = SuspendObjectForm()

    if request.method == 'POST':
        suspend_form = SuspendObjectForm(request.POST)
        if suspend_form.is_valid():
            reason = suspend_form.cleaned_data['reason']
            ban_user = suspend_form.cleaned_data['ban_user']
            ban_user_duration_days = suspend_form.cleaned_data['ban_user_duration_days']

            ar_text_object.visibility = 'Suspended'
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f"{timestamp}: Suspended by {request.user.username} - Reason: {reason}"
            ar_text_object.system_notes.append(note)
            ar_text_object.save()

            if ban_user:
                user_to_ban = ar_text_object.creator
                user_to_ban.account_status = 'Suspended'
                user_to_ban.ban_expiration = timezone.now() + timezone.timedelta(days=ban_user_duration_days)
                user_to_ban.save()

                ban_reason = f"User banned due to suspension of AR Text Object ID {ar_text_object.id}."
                ban_notification = f"""
                    Your account has been suspended due to a violation of our terms of service.
                    Suspension Reason: {ban_reason},
                    Suspension Start Date: {timestamp},
                    Suspension Duration: {ban_user_duration_days} days,
                    If you believe this was an error, please use the appeal button on the object page.
                    """
                Notification.objects.create(
                    recipient=user_to_ban,
                    title='Account Suspension Notice',
                    message=ban_notification
                )

            messages.success(request, 'AR Text Object suspended successfully.')
            return redirect('ar_text_object_detail', pk=ar_text_object.pk)





