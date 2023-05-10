from django.urls import path
from . import views
from .api.views import CustomerList, CustomerDetail


app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),

    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),

    path('customers/', CustomerList.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetail.as_view(), name='customer-detail'),
]
