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

        # Проходим по всем категориям этой новости
        for category in post.categories.all():
            # Находим всех пользователей, подписанных на эту категорию
            for subscriber in category.subscribers.all():
                # Проверяем, что у пользователя вообще указан email
                if subscriber.email:
                    subject = f'Новая статья: {post.title}'

                    # Генерируем HTML-контент письма из шаблона
                    html_content = render_to_string(
                        'emails/new_post_notification.html',
                        {
                            'post': post,
                            'user': subscriber,
                            'category_name': category.name,
                            'link': f"{settings.SITE_URL}{post.get_absolute_url()}",
                        }
                    )

                    # Создаем объект письма
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body="Текстовая версия письма для клиентов без поддержки HTML.",
                        from_email=settings.DEFAULT_FROM_EMAIL,  # ИСПРАВЛЕННАЯ СТРОКА
                        to=[subscriber.email],
                    )

                    # Подключаем HTML-версию письма
                    msg.attach_alternative(html_content, "text/html")

                    try:
                        # Отправляем письмо (fail_silently=False - выведет ошибку в терминал)
                        msg.send(fail_silently=False)
                        print(f"✅ УСПЕХ: Письмо отправлено на {subscriber.email} о статье '{post.title}'")
                    except Exception as e:
                        print(f"❌ ОШИБКА ОТПРАВКИ: {e}")


@receiver(pre_save, sender=Post)
def limit_posts_per_author(sender, instance, **kwargs):
    """
    Сигнал: Ограничивает создание постов до 3 штук в сутки на одного автора.
    """
    # Проверяем, что это новый пост, а не редактирование старого
    if instance.pk is None:
        author = instance.author

        # Определяем временной интервал (последние 24 часа)
        time_threshold = timezone.now() - timedelta(days=1)

        # Считаем количество постов этого автора за последние сутки
        posts_count_today = Post.objects.filter(
            author=author,
            created_at__gte=time_threshold # created_at должно быть больше или равно порогу
        ).count()

        # Если лимит (3 поста) уже исчерпан, вызываем ошибку
        if posts_count_today >= 3:
            raise ValidationError(
                f"Лимит исчерпан. Вы можете создавать не более 3 постов в сутки. "
                f"Сегодня уже создано: {posts_count_today}."
            )