from django.urls import path, include
from . import views
from .api import UserList, UserDetail, RankList, RankDetail, AccountList, AccountDetail, CustomerList, CustomerDetail, \
    TransactionList, TransactionDetail

app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction_details/<int:transaction>/', views.transaction_details, name='transaction_details'),
    path('account_details/<int:pk>/', views.account_details, name='account_details'),
    path('make_transfer/', views.make_transfer, name='make_transfer'),
    path('make_loan/', views.make_loan, name='make_loan'),

    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer_account/', views.customer_account, name='customer_account'),

    path('staff_new_customer/', views.staff_new_customer, name='staff_new_customer'),
    path('staff_customer_details/<int:pk>/', views.staff_customer_details, name='staff_customer_details'),
    path('staff_new_account_partial/<int:user>/', views.staff_new_account_partial, name='staff_new_account_partial'),
    path('staff_account_list_partial/<int:pk>/', views.staff_account_list_partial, name='staff_account_list_partial'),
    path('staff_account_details/<int:pk>/', views.staff_account_details, name='staff_account_details'),

    path('send_transfer_request/', views.send_transfer_request, name='send_transfer_request'),
    path('foreign_transfer_details/', views.foreign_transfer_details, name='foreign_transfer_details'),
    path('api/receive_transfer/', views.receive_transfer, name='receive_transfer'),

    path('user/api/v1/', UserList.as_view()),
    path('user/api/v1/<int:pk>/', UserDetail.as_view()),
    path('user/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('rank/api/v1/', RankList.as_view()),
    path('rank/api/v1/<int:pk>/', RankDetail.as_view()),
    path('rank/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('account/api/v1/', AccountList.as_view()),
    path('account/api/v1/<int:pk>/', AccountDetail.as_view()),
    path('account/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('customer/api/v1/', CustomerList.as_view()),
    path('customer/api/v1/<int:pk>/', CustomerDetail.as_view()),
    path('customer/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('transaction/api/v1/', TransactionList.as_view()),
    path('transaction/api/v1/<int:pk>/', TransactionDetail.as_view()),
    path('transaction/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
]
