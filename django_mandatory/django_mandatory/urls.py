from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('bank_app.urls')),
    path('^social/', include('social.apps.django_app.urls', namespace='social'))
]
