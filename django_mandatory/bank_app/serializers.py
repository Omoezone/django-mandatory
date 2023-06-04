from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Rank, Account, Customer, Transaction, TransferModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True}
        }


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    movements = serializers.SerializerMethodField()
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'name', 'is_loan', 'user', 'movements', 'balance')

    def get_movements(self, obj):
        return TransactionSerializer(obj.movements, many=True).data


class CustomerSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True, read_only=True)
    default_account = AccountSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'user', 'phone', 'rank', 'full_name', 'accounts', 'can_make_loan', 'default_account')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransferModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferModel
        fields = ('amount', 'debit_account', 'debit_description', 'credit_account', 'credit_description',
                  'idempotence', 'state')

