from django.urls import path
from . import views


app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
]