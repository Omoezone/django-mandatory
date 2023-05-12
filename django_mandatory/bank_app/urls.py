from django.urls import path, include
from . import views
from api import *

app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('/rank/api/v1/', RankList.as_view()),
    path('/rank/api/v1/<int:pk>', RankDetail.as_view()),
    path('/rank/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('/account/api/v1/', AccountList.as_view()),
    path('/account/api/v1/<int:pk>', AccountDetail.as_view()),
    path('/account/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('/customer/api/v1/', CustomerList.as_view()),
    path('/customer/api/v1/<int:pk>/', CustomerDetail.as_view()),
    path('/customer/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
    path('/transaction/api/v1/', TransactionList.as_view()),
    path('/transaction/api/v1/<int:pk>', TransactionDetail.as_view()),
    path('/transaction/api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
]
