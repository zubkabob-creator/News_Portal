from django.contrib import admin
from django.urls import path, include
from .models import Author, Category, Post, PostCategory, Comment

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)

urlpatterns = [
   path('admin/', admin.site.urls),
   path('pages/', include('django.contrib.flatpages.urls')),  # < вот тут
]