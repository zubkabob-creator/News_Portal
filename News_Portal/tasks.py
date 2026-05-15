from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from .models import Post, Category  # Импортируем модели
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


@shared_task
def send_new_post_notifications_task(post_id):

    try:
        post = Post.objects.get(id=post_id)

        for category in post.categories.all():
            for subscriber in category.subscribers.all():
                if subscriber.email:
                    subject = f'Новая статья: {post.title}'

                    html_content = render_to_string(
                        'emails/new_post_notification.html',
                        {
                            'post': post,
                            'user': subscriber,
                            'category_name': category.name,
                            'site_url': Site.objects.get_current().domain,
                        }
                    )

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body="Текстовая версия письма...",
                        from_email=f"NewsSite <{settings.DEFAULT_FROM_EMAIL}>",
                        to=[subscriber.email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
    except Post.DoesNotExist:
        return


@shared_task
def send_weekly_digest_task():

    week_ago = timezone.now() - timedelta(days=7)

    categories_with_new_posts = Category.objects.filter(post__created_at__gte=week_ago).distinct()

    for category in categories_with_new_posts:
        subscribers = category.subscribers.all()
        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=week_ago,
        ).order_by('-created_at')

        if not subscribers.exists() or not new_posts.exists():
            continue

        for subscriber in subscribers:
            if not subscriber.email:
                continue

            subject = f'Еженедельный дайджест: Новые статьи в "{category.name}"'

            html_content = render_to_string(
                'emails/weekly_digest.html',
                {
                    'posts': new_posts,
                    'user': subscriber,
                    'category_name': category.name,
                    'site_url': Site.objects.get_current().domain,
                    'week_ago': week_ago.date(),
                }
            )

            from_email = f"NewsSite <{settings.DEFAULT_FROM_EMAIL}>"

            msg = EmailMultiAlternatives(
                subject=subject,
                body="Текстовая версия дайджеста...",
                from_email=from_email,
                to=[subscriber.email],
                reply_to=[settings.DEFAULT_FROM_EMAIL],
            )
            msg.attach_alternative(html_content, "text/html")

            try:
                msg.send(fail_silently=False)
                print(f"  ✅ Еженедельный дайджест отправлен на {subscriber.email}")
            except Exception as e:
                print(f"  ❌ ОШИБКА отправки дайджеста: {e}")