"""hairdressers_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from hairdressers_project import settings
from users_app.views import page_400_view, page_403_view, page_404_view, page_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users_app.urls')),
    path('', include('selection_app.urls')),
    path('captcha/', include('captcha.urls')),
]

handler400 = page_400_view
handler403 = page_403_view
handler404 = page_404_view
handler500 = page_500_view

if settings.DEBUG:
    urlpatterns = [
                      path('__debug__/', include('debug_toolbar.urls')),
                  ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
