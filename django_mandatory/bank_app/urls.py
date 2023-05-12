from django.urls import path
from . import views


app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction_details/<int:transaction>/', views.transaction_details, name='transaction_details'),
    path('account_details/<int:pk>/', views.account_details, name='account_details'),
    path('make_transfer/', views.make_transfer, name='make_transfer'),

    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer_account/', views.customer_account, name='customer_account'),

    path('staff_new_customer/', views.staff_new_customer, name='staff_new_customer'),
    path('staff_customer_details/<int:pk>/', views.staff_customer_details, name='staff_customer_details'),
    path('staff_new_account_partial/<int:user>/', views.staff_new_account_partial, name='staff_new_account_partial'),
    path('staff_account_list_partial/<int:pk>/', views.staff_account_list_partial, name='staff_account_list_partial'),
    path('staff_account_details/<int:pk>/', views.staff_account_details, name='staff_account_details'),
]
