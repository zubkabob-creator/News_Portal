from datetime import datetime
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .tasks import send_new_post_notifications_task
from .models import Post, Author, Category
from .filters import NewsFilter
from django_filters.views import FilterView
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class NewsSearch(FilterView):
    filterset_class = NewsFilter
    template_name = 'news/search.html'
    context_object_name = 'news'
    paginate_by = 10
    ordering = ['-created_at']

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['queryset'] = Post.objects.order_by('-created_at')  # Обязательно сортируем queryset
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class news(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        self.filterset = NewsFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        context['total_news_count'] = Post.objects.count()

        return context


class newsDetail(DetailView):
    model = Post
    template_name = 'newsDetail.html'
    context_object_name = 'newsDetail'

    def get_object(self, queryset=None):
        # obj = super().get_object(queryset)
        # cache_key = f'post_{obj.pk}_detail'
        # cached_version = cache.get(cache_key)
        # if cached_version is None:
        #     rendered_html = render_to_string(self.template_name, {'object': obj})
        #     cache.set(cache_key, rendered_html, timeout=None)  # Бессрочное хранение
        #     return obj
        # return mark_safe(cached_version)
        return super().get_object(queryset)

class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_create.html'
    permission_required = 'News_Portal.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.created_at = timezone.now()
        post.type = Post.NEWS
        current_user = self.request.user
        author, created = Author.objects.get_or_create(user=current_user)
        post.author = author
        response = super().form_valid(form)
        send_new_post_notifications_task.delay(self.object.id)
        return response


class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_create.html'
    permission_required = 'News_Portal.change_post'


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'

    success_url = reverse_lazy('news_list')



class ArticleCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'article_create.html'
    permission_required = 'News_Portal.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.created_at = timezone.now()
        post.type = Post.NEWS
        current_user = self.request.user
        author, created = Author.objects.get_or_create(user=current_user)
        post.author = author
        response = super().form_valid(form)
        send_new_post_notifications_task.delay(self.object.id)
        return response


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'article_create.html'
    permission_required = 'News_Portal.change_post'


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'

    success_url = reverse_lazy('news_list')


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


class CategorySubscribeView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))

        if request.user in category.subscribers.all():
            category.subscribers.remove(request.user)
        else:
            category.subscribers.add(request.user)

        return redirect(request.META.get('HTTP_REFERER', 'news_list'))