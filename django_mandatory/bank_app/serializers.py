from rest_framework import serializers
from .models import Rank, Account, Customer, Transaction, UID


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
        fields = ('id', 'account', 'amount', 'description', 'transaction')

    def process_transactions(data1, data2):
        serializer1 = TransactionSerializer(data=data1)
        serializer1.is_valid(raise_exception=True)
        validated_data1 = serializer1.validated_data

        serializer2 = TransactionSerializer(data=data2)
        serializer2.is_valid(raise_exception=True)
        validated_data2 = serializer2.validated_data

        return validated_data1, validated_data2
