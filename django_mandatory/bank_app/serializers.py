from rest_framework import serializers
from .models import Rank, Account, Customer, Transaction


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ('id', 'name', 'value')


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'is_loan', 'user', 'movements', 'balance')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'user', 'phone', 'rank', 'full_name', 'accounts', 'can_make_loan', 'default_account')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'description', 'date', 'account', 'transaction')
