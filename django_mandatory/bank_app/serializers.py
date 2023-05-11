from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'phone', 'rank', 'full_name', 'can_make_loan', 'default_account')
        model = Customer
