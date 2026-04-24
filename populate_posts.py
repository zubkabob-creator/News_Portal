import os
import django
import random
import faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')
django.setup()

from News_Portal.models import Post, Author, Category, PostCategory


def generate_posts(num_posts=100):
    fake = faker.Faker('ru_RU')
    print(f"Путь к модулю Faker: {faker.__file__}")
    print(f"Объект Faker: {fake}")
    print(f"Начинаю генерацию {num_posts} постов (статей и новостей)...")
    print(f"Версия Django: {django.get_version()}")



    try:
        all_authors = list(Author.objects.all())
        all_categories = list(Category.objects.all())

        if not all_authors or not all_categories:
            print("Ошибка: В базе данных нет авторов или категорий для привязки.")
            return

    except Exception as e:
        print(f"Произошла ошибка при обращении к базе данных: {e}")
        return

    for i in range(num_posts):
        title = fake.sentence(nb_words=6, variable_nb_words=True)
        text = "\n\n".join(fake.texts(nb_texts=3, max_nb_chars=800))

        author = random.choice(all_authors)

        post_type = random.choice([Post.ARTICLE, Post.NEWS])

        post = Post.objects.create(
            author=author,
            type=post_type,
            title=title,
            text=text,
            rating=random.randint(-10, 50)
        )

        selected_categories = random.sample(all_categories, k=random.randint(1, 3))

        post.categories.set(selected_categories)

        if (i + 1) % 10 == 0:
            print(f"Сгенерировано {i + 1} постов...")

    print(f"✅ УСПЕХ! Сгенерировано {num_posts} постов.")


if __name__ == '__main__':
    generate_posts(100)