from django.urls import path
from .views import (
    news, newsDetail,
    NewsSearch, NewsCreateView,
    ArticleCreateView, NewsUpdateView,
    ArticleUpdateView, NewsDeleteView,
    ArticleDeleteView
)

urlpatterns = [
    path('', news.as_view(), name='news_list'),
    path('search/', NewsSearch.as_view(template_name='news/search.html'), name='news_search'),
    path('<int:pk>/', newsDetail.as_view(), name='news_detail'),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
]
