
import django.contrib.messages as messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import models

from pataverse.utils import set_base_template

from apps.users.models import CustomUser

from .models import Friendship, FriendRequest
from .forms import FriendRequestForm

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        form = FriendRequestForm(request.POST)
        if form.is_valid():
            friend_request = form.save(commit=False)
            friend_request.sender = request.user
            friend_request.save()
            messages.success(request, 'Friend request sent successfully.')
            return redirect('social:friend_list')
    else:
        form = FriendRequestForm()
    
    context = {
        'form': form,
        'base_template': set_base_template(request.user),
    }
    return render(request, 'social/send_friend_request.html', context)


@login_required
def accept_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user, status='pending')
        friend_request.status = 'accepted'
        friend_request.updated_at = timezone.now()
        friend_request.save()

        # Create Friendship
        friendship = Friendship.objects.create(
            user_1=friend_request.sender,
            user_2=friend_request.receiver,
            user_1_status='accepted',
            user_2_status='accepted'
        )

        messages.success(request, 'Friend request accepted.')
    except FriendRequest.DoesNotExist:
        messages.error(request, 'Friend request not found or already processed.')

    return redirect('social:friend_list')


@login_required
def decline_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user, status='pending')
        friend_request.status = 'declined'
        friend_request.updated_at = timezone.now()
        friend_request.save()
        messages.success(request, 'Friend request declined.')
    except FriendRequest.DoesNotExist:
        messages.error(request, 'Friend request not found or already processed.')

    return redirect('social:friend_list')


@login_required
def friend_list(request):
    friendships = Friendship.objects.filter(
        models.Q(user_1=request.user, user_1_status='accepted') |
        models.Q(user_2=request.user, user_2_status='accepted')
    )

    friends = []
    for friendship in friendships:
        if friendship.user_1 == request.user:
            friends.append(friendship.user_2)
        else:
            friends.append(friendship.user_1)

    pending_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')

    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'base_template': set_base_template(request.user),
    }
    return render(request, 'social/friend_list.html', context)


@login_required
def remove_friend(request, friend_id):
    try:
        friend = CustomUser.objects.get(id=friend_id)
        friendship = Friendship.objects.get(
            (models.Q(user_1=request.user, user_2=friend) |
            models.Q(user_1=friend, user_2=request.user)),
            models.Q(user_1_status='accepted', user_2_status='accepted')
        )
        friendship.delete()
        messages.success(request, f'You have removed {friend.username} from your friends list.')
    except (CustomUser.DoesNotExist, Friendship.DoesNotExist):
        messages.error(request, 'Friend not found or not in your friends list.')

    return redirect('social:friend_list')


@login_required
def cancel_friend_request(request, request_id):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, sender=request.user, status='pending')
        friend_request.delete()
        messages.success(request, 'Friend request canceled.')
    except FriendRequest.DoesNotExist:
        messages.error(request, 'Friend request not found or already processed.')

    return redirect('social:friend_list')


@login_required
def block_user(request, user_id):
    try:
        user_to_block = CustomUser.objects.get(id=user_id)
        friendship, created = Friendship.objects.get_or_create(
            (models.Q(user_1=request.user, user_2=user_to_block) |
            models.Q(user_1=user_to_block, user_2=request.user))
        )
        if friendship.user_1 == request.user:
            friendship.user_1_status = 'blocked'
        else:
            friendship.user_2_status = 'blocked'
        friendship.save()
        messages.success(request, f'You have blocked {user_to_block.username}.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')

    return redirect('social:friend_list')


@login_required
def unblock_user(request, user_id):
    try:
        user_to_unblock = CustomUser.objects.get(id=user_id)
        friendship = Friendship.objects.get(
            (models.Q(user_1=request.user, user_2=user_to_unblock) |
            models.Q(user_1=user_to_unblock, user_2=request.user))
        )
        if friendship.user_1 == request.user and friendship.user_1_status == 'blocked':
            friendship.user_1_status = 'accepted'
        elif friendship.user_2 == request.user and friendship.user_2_status == 'blocked':
            friendship.user_2_status = 'accepted'
        friendship.save()
        messages.success(request, f'You have unblocked {user_to_unblock.username}.')
    except (CustomUser.DoesNotExist, Friendship.DoesNotExist):
        messages.error(request, 'User not found or not blocked.')

    return redirect('social:friend_list')       


@login_required
def blocked_list(request):
    blocked_friendships = Friendship.objects.filter(
        (models.Q(user_1=request.user, user_1_status='blocked') |
        models.Q(user_2=request.user, user_2_status='blocked'))
    )

    blocked_users = []
    for friendship in blocked_friendships:
        if friendship.user_1 == request.user:
            blocked_users.append(friendship.user_2)
        else:
            blocked_users.append(friendship.user_1)

    context = {
        'blocked_users': blocked_users,
        'base_template': set_base_template(request.user),
    }
    return render(request, 'social/blocked_list.html', context)


@login_required
def friend_requests_sent(request):
    sent_requests = FriendRequest.objects.filter(sender=request.user, status='pending')

    context = {
        'sent_requests': sent_requests,
        'base_template': set_base_template(request.user),
    }
    return render(request, 'social/friend_requests_sent.html', context)


@login_required
def friend_requests_received(request):
    received_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')

    context = {
        'received_requests': received_requests,
        'base_template': set_base_template(request.user),
    }
    return render(request, 'social/friend_requests_received.html', context)




