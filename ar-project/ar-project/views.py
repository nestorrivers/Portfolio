from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

import django.contrib.messages as messages

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from apps.objects.models import ARTextObject

from .utils import set_base_template

from apps.notifications.models import Notification
from apps.channels.models import ARChannel




@login_required(login_url='/login/')
def home_redirect(request):
    user = request.user

    if user.user_type == 'Admin':
        return redirect(reverse('admin_home'))
    elif user.user_type == 'User':
        return redirect(reverse('user_home'))


@login_required(login_url='/login/')
def admin_home(request):
    user = request.user

    if user.user_type != 'Admin':
        return redirect(reverse('user_home'))

    notifications = Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')[:10]
    recent_objects = []  # Placeholder for recent objects logic
    recent_objects.append(ARTextObject.objects.order_by('-created_at')[:5])


    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'notifications': notifications,
        'recent_objects': recent_objects,
    }

    return render(request, 'dashboards/admin-dashboard.html', context)


@login_required(login_url='/login/')
def user_home(request):
    user = request.user

    if user.user_type != 'User':
        return redirect(reverse('admin_home'))
    
    notifications = Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')
    recent_objects = []  # Placeholder for recent objects logic
    recent_objects.append(ARTextObject.objects.filter(creator=user).order_by('-created_at')[:5])

    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'notifications': notifications,
        'recent_objects': recent_objects,
    }

    return render(request, 'dashboards/user-dashboard.html', context)
