from django.urls import path, include
from . import views
from .api import CustomerList, CustomerDetail

app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('api/v1/', CustomerList.as_view()),
    path('api/v1/<int:pk>/', CustomerDetail.as_view()),
    path('api/v1/dj-rest-auth/', include('dj_rest_auth.urls')),
]
