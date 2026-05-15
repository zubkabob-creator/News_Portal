from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import PostCategory, Post


@receiver(m2m_changed, sender=PostCategory)
def send_new_post_notifications(sender, instance, action, **kwargs):
    if action == 'post_add':
        post = instance

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
                            'link': f"{settings.SITE_URL}{post.get_absolute_url()}",
                        }
                    )

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body="Текстовая версия письма для клиентов без поддержки HTML.",
                        from_email=settings.DEFAULT_FROM_EMAIL,  # ИСПРАВЛЕННАЯ СТРОКА
                        to=[subscriber.email],
                    )

                    msg.attach_alternative(html_content, "text/html")

                    try:
                        msg.send(fail_silently=False)
                        print(f"✅ УСПЕХ: Письмо отправлено на {subscriber.email} о статье '{post.title}'")
                    except Exception as e:
                        print(f"❌ ОШИБКА ОТПРАВКИ: {e}")


@receiver(pre_save, sender=Post)
def limit_posts_per_author(sender, instance, **kwargs):

    if instance.pk is None:
        author = instance.author

        time_threshold = timezone.now() - timedelta(days=1)

        posts_count_today = Post.objects.filter(
            author=author,
            created_at__gte=time_threshold
        ).count()

        if posts_count_today >= 3:
            raise ValidationError(
                f"Лимит исчерпан. Вы можете создавать не более 3 постов в сутки. "
                f"Сегодня уже создано: {posts_count_today}."
            )