from rest_framework import serializers
from models import Rank
from models import Account
from models import Customer
from models import Transaction


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', '')
        model = Rank


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', '')
        model = Account


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'phone', 'rank', 'full_name', 'can_make_loan', 'default_account')
        model = Customer


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', '')
        model = Transaction
