import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

logger = logging.getLogger(__name__)



def send_weekly_digest_job():
    print("--- ТЕСТ: Запуск функции МАССОВОЙ рассылки ---")
    week_ago = timezone.now() - timedelta(days=7)

    from News_Portal.models import Category, Post

    categories_with_new_posts = Category.objects.filter(post__created_at__gte=week_ago).distinct()

    for category in categories_with_new_posts:
        subscribers = category.subscribers.all()
        if not subscribers.exists():
            print(f"  В категории '{category.name}' нет подписчиков.")
            continue

        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=week_ago,
        ).order_by('-created_at')

        if not new_posts.exists():
            print(f"  В категории '{category.name}' нет новых постов.")
            continue

        print(
            f"  Категория '{category.name}': найдено {new_posts.count()} новых постов. Начинаем отправку {subscribers.count()} подписчикам.")

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

            from_email = settings.DEFAULT_FROM_EMAIL

            msg = EmailMultiAlternatives(
                subject=subject,
                body="Текстовая версия дайджеста...",
                from_email=from_email,
                to=[subscriber.email],
                reply_to=[from_email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.extra_headers = {'List-Unsubscribe': f'<mailto:{from_email}?subject=unsubscribe>'}

            try:
                msg.send(fail_silently=False)
                print(f"  ✅ ПИСЬМО ОТПРАВЛЕНО на {subscriber.email}")
            except Exception as e:
                print(f"  ❌ ОШИБКА ОТПРАВКИ для {subscriber.email}: {e}")

    print("--- ТЕСТ: Цикл массовой рассылки завершен ---")


def delete_old_job_executions(max_age=604_800):

    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler to handle scheduled tasks."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_digest_job,
            trigger=CronTrigger(day_of_week="sun", hour="06", minute="00"),
            id="weekly_digest_job",
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'weekly_digest_job' with 15-second interval.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        try:
            print("Starting scheduler...")
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Stopping scheduler...")
            scheduler.shutdown()
            print("Scheduler shut down successfully!")