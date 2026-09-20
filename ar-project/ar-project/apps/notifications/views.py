
import django.contrib.messages as messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone

from ar_project.utils import set_base_template

from apps.users.models import CustomUser

from .models import Notification, NewsPost
from .forms import NewsPostForm


def notification_view(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found.')
        return redirect('home')

    # Mark the notification as read
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()

    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'notification': notification,
    }

    return render(request, 'notifications/notification-view.html', context)


@login_required
def create_news_post(request):
    if request.user.user_type != 'Admin':
        messages.error(request, 'You do not have permission to create news posts.')
        return redirect('home')

    form = NewsPostForm()
    if request.method == 'POST':
        form = NewsPostForm(request.POST)
        if form.is_valid():
            news_post = form.save(commit=False)
            news_post.author = request.user
            news_post.save()

            users = CustomUser.objects.values_list("id", flat=True)
            notifications = [
                Notification(
                    recipient_id=user_id,
                    title='News Post Created',
                    message=f'Your news post \"{news_post.title}\" has been created successfully.',
                    action_url=f'{settings.SITE_URL}/news/{news_post.slug}/',
                    action_button_text='Read More',
                )
                for user_id in users
            ]

            Notification.objects.bulk_create(notifications, batch_size=500)
            messages.success(request, 'News post created successfully.')
            return redirect('news-post-detail', slug=news_post.slug)

    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'form': form,
    }
    return render(request, 'notifications/create-news-post.html', context)


@login_required
def news_post_list(request):
    news_posts = NewsPost.objects.filter(is_published=True).order_by('-published_at')

    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'news_posts': news_posts,
    }
    return render(request, 'notifications/news-post-list.html', context)


@login_required
def news_post_detail(request, slug):
    try:
        news_post = NewsPost.objects.get(slug=slug, is_published=True)
    except NewsPost.DoesNotExist:
        messages.error(request, 'News post not found.')
        return redirect('news-post-list')

    base_template = set_base_template(request)
    context = {
        'base_template': base_template,
        'news_post': news_post,
    }
    return render(request, 'notifications/news-post-detail.html', context)