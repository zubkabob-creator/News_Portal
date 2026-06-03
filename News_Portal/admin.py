from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment
from django.utils.html import format_html
from django.urls import reverse

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'preview_text', 'category_list')
    list_filter = ('author', 'categories', 'created_at')
    search_fields = ('title', 'text')
    ordering = ('-created_at',)

    def category_list(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    category_list.short_description = 'Categories'

    def preview_text(self, obj):
        return obj.preview()
    preview_text.short_description = 'Preview'

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'show_posts_link')
    list_filter = ('user',)

    def show_posts_link(self, obj):
        count = obj.post_set.count()
        url = (
            reverse("admin:News_Portal_post_changelist")
            + "?author__id__exact="
            + str(obj.id)
        )
        return format_html('<a href="{}">{} Posts</a>', url, count)
    show_posts_link.allow_tags = True
    show_posts_link.short_description = "Posts"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscriber_count')
    list_filter = ('subscribers',)

    def subscriber_count(self, obj):
        return obj.subscribers.count()
    subscriber_count.short_description = 'Subscribers'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'rating', 'short_text')
    list_filter = ('post', 'user', 'created_at')
    search_fields = ('text',)

    def short_text(self, obj):
        return obj.text[:50] + '...'
    short_text.short_description = 'Text Preview'

admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment, CommentAdmin)