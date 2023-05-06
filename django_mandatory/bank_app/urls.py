from django.urls import path
from . import views


app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='a'),

    path('customer_account/', views.customer_account, name='customer_account'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer_transaction/', views.customer_transaction, name='customer_transaction'),
    path('customer_account/', views.customer_account, name='customer_account'),
    path('account/<int:pk>/', views.account_single, name='account_single')

]
