from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(tf_urls)),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('bank_app.urls'))
]
