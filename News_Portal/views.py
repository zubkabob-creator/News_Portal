from datetime import datetime
from django.views.generic import ListView, DetailView
from .models import Post

class news(ListView):
    model = Post
    ordering = ['-created_at']
    template_name = 'news.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context


class newsDetail(DetailView):
    model = Post
    template_name = 'newsDetail.html'
    context_object_name = 'newsDetail'
