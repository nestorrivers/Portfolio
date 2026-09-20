
import django.contrib.messages as messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from pataverse.utils import set_base_template

from django.conf import settings

from django.utils import timezone

from .models import ARChannel
from .forms import ARChannelForm


@login_required()
def create_channel(request):

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to create a channel.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ARChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.creator = request.user
            note = f"{timezone.now()}: Channel created by {request.user.username}."
            channel.system_notes.append(note)
            channel.save()
            messages.success(request, 'Channel created successfully!')
            return redirect('channel_detail', slug=channel.slug)
    else:
        form = ARChannelForm()
    return render(request, 'channels/channel-form.html', {'form': form})


@login_required()
def channel_detail(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug)
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found.')
        return redirect('home')
    
    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to view this channel.')
        return redirect('home')

    return render(request, 'channels/view-channel-details.html', {'channel': channel})


@login_required()
def edit_channel(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug)
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found.')
        return redirect('home')

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to edit this channel.')
        return redirect('home')

    if request.method == 'POST':
        form = ARChannelForm(request.POST, instance=channel)
        if form.is_valid():
            channel = form.save()
            changed_fields = []
            for field in form.changed_data:
                changed_fields.append(field)
            if changed_fields:
                note = f"{timezone.now()}: Channel edited by {request.user.username}. Fields changed: {', '.join(changed_fields)}."
            else:
                note = f"{timezone.now()}: Channel edited by {request.user.username}. No fields changed."
            channel.system_notes.append(note)
            channel.save()
            messages.success(request, 'Channel updated successfully!')
            return redirect('channel_detail', slug=channel.slug)
    else:
        form = ARChannelForm(instance=channel)
    
    return render(request, 'channels/channel-form.html', {'form': form, 'channel': channel})


@login_required()
def delete_channel(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug)
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found.')
        return redirect('home')

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to delete this channel.')
        return redirect('home')

    if request.method == 'POST':
        channel.delete()
        messages.success(request, 'Channel deleted successfully!')
        return redirect('home')

    return render(request, 'channels/delete_channel.html', {'channel': channel})


@login_required()
def deactivate_channel(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug)
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found.')
        return redirect('home')

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to deactivate this channel.')
        return redirect('home')

    channel.is_active = False
    note = f"{timezone.now()}: Channel deactivated by {request.user.username}."
    channel.system_notes.append(note)
    channel.save()
    messages.success(request, 'Channel deactivated successfully!')
    return redirect('channel_detail', slug=channel.slug)


@login_required()
def activate_channel(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug)
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found.')
        return redirect('home')

    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to activate this channel.')
        return redirect('home')

    channel.is_active = True
    note = f"{timezone.now()}: Channel activated by {request.user.username}."
    channel.system_notes.append(note)
    channel.save()
    messages.success(request, 'Channel activated successfully!')
    return redirect('channel_detail', slug=channel.slug)



@login_required()
def channel_list_admin(request):
    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to view channels.')
        return redirect('home')

    channels = ARChannel.objects.all().order_by('-created_at')

    context = {
        'base_template': set_base_template(request),
        'channels': channels
    }

    return render(request, 'channels/channel-list-admin.html', context)


@login_required()
def channel_list_user(request):
    channels = ARChannel.objects.filter(status='Active').order_by('-created_at')
    context = {
        'base_template': set_base_template(request),
        'channels': channels
    }
    return render(request, 'channels/channel-list-user.html', context)


@login_required()
def channel_ar_viewer(request, slug):
    try:
        channel = ARChannel.objects.get(slug=slug, status='Active')
    except ARChannel.DoesNotExist:
        messages.error(request, 'Channel not found or inactive.')
        return redirect('home')

    return render(request, 'channels/channel-viewer-ar.html', {'channel': channel})


@login_required()
def friends_channel_viewer(request):
    
    return render(request, 'channels/friends-viewer-ar.html')




