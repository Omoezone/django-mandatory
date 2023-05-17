from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Rank, Account, Customer, Transaction
from .serializers import RankSerializer, AccountSerializer, CustomerSerializer, TransactionSerializer
from .permissions import IsOwnerOrNoAccess


class RankList(generics.ListCreateAPIView):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer

#    def get_queryset(self):
#        queryset = Rank.objects.filter(user=self.request.user)
#        return queryset


class RankDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


class AccountList(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

#    def get_queryset(self):
#        queryset = Account.objects.filter(user=self.request.user)
#        return queryset


class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

#    def get_queryset(self):
#        queryset = Customer.objects.filter(user=self.request.user)
#        return queryset


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class TransactionList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = TransactionSerializer

#    def get_queryset(self):
#        queryset = Rank.objects.filter(user=self.request.user)
#        return queryset


class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = TransactionSerializer
