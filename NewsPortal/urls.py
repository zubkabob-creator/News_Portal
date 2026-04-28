from django.contrib import admin
from django.urls import path, include
from News_Portal.views import upgrade_me
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('news/', include('News_Portal.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('protect.urls')),
    path('protect/logout/', LogoutView.as_view(template_name = 'protect/logout.html'), name='logout'),
]

