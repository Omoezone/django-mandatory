from rest_framework import serializers
from models import Rank, Account, Customer, Transaction


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'value')
        model = Rank


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'is_loan', 'user', 'movements', 'balance')
        model = Account


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'phone', 'rank', 'full_name', 'can_make_loan', 'default_account')
        model = Customer


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'transaction_type', 'amount', 'description', 'date', 'account', 'uid')
        model = Transaction
