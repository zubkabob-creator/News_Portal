from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('news/', include('News_Portal.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

