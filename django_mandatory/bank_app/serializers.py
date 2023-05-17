from rest_framework import serializers
from .models import Rank, Account, Customer, Transaction


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
