from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    """
    Модель автора. Связывает пользователя с его рейтингом.
    """
    # Связь «один к одному» с встроенной моделью User.
    # При удалении пользователя, автор тоже удаляется (CASCADE).
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Рейтинг автора (суммируется из рейтингов постов и комментариев).
    rating = models.IntegerField(default=0)

    def update_rating(self):
        """
        Обновляет рейтинг автора по формуле:
        Рейтинг = (Суммарный рейтинг всех статей автора * 3)
                  + (Суммарный рейтинг всех комментариев автора)
                  + (Суммарный рейтинг всех комментариев к статьям автора)
        """
        # 1. Суммарный рейтинг всех статей автора * 3
        post_rating = self.post_set.filter(type='AR').aggregate(models.Sum('rating'))['rating__sum'] or 0
        post_rating *= 3

        # 2. Суммарный рейтинг всех комментариев автора
        comment_rating = self.user.comment_set.aggregate(models.Sum('rating'))['rating__sum'] or 0

        # 3. Суммарный рейтинг всех комментариев к статьям автора
        posts_comments_rating = Comment.objects.filter(
            post__author=self, post__type='AR'
        ).aggregate(models.Sum('rating'))['rating__sum'] or 0

        # Итоговый рейтинг
        self.rating = post_rating + comment_rating + posts_comments_rating
        self.save()


class Category(models.Model):
    """
    Категория новостей/статей (например: Спорт, Политика).
    """
    # Название категории. Должно быть уникальным.
    name = models.CharField(max_length=255, unique=True)


class Post(models.Model):
    """
    Модель поста. Может быть статьей или новостью.
    """
    # Выбор типа поста: статья или новость.
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPE_CHOICES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=POST_TYPE_CHOICES)

    # Дата создания добавляется автоматически при сохранении.
    created_at = models.DateTimeField(auto_now_add=True)

    # Заголовок и текст поста.
    title = models.CharField(max_length=255)
    text = models.TextField()

    # Рейтинг поста (лайки/дизлайки).
    rating = models.IntegerField(default=0)

    # Связь «многие ко многим» с категориями через промежуточную модель PostCategory.
    categories = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        """Увеличивает рейтинг поста на 1."""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг поста на 1."""
        self.rating -= 1
        self.save()

    def preview(self):
        """
        Возвращает превью статьи: первые 124 символа текста и многоточие.
        """
        return self.text[:124] + '...'


class PostCategory(models.Model):
    """
    Промежуточная модель для связи Post и Category.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    """
    Модель комментария к посту.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # Связь с пользователем, оставившим комментарий.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField()

    # Дата создания комментария.
    created_at = models.DateTimeField(auto_now_add=True)

    rating = models.IntegerField(default=0)

    def like(self):
        """Увеличивает рейтинг комментария на 1."""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг комментария на 1."""
        self.rating -= 1
        self.save()
