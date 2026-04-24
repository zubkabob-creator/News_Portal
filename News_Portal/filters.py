import django_filters
from .models import Post, Author
from django import forms
from datetime import datetime
from django.utils.timezone import make_aware


class NewsFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        empty_label='Все авторы',
        label='Фильтр по авторам',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='iregex',
        label='Фильтр по заголовку',
    widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Начните вводить заголовок...'})
    )

    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата публикации (позже)',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['author', 'title', 'created_after']


