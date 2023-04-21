from django.db import models, transaction
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from decimal import Decimal


class UID(models.Model):
    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    def __str__(self):
        return f'{self.pk}'


class Rank(models.Model):
    name = models.CharField(max_length=15, unique=True, db_index=True)
    value = models.IntegerField(unique=True, db_index=True)

    def __str__(self):
        return f'{self.name} : {self.value}'


class Account(models.Model):
    name = models.CharField(max_length=25)
    is_loan = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def movements(self) -> QuerySet:
        return Transaction.objects.filter(account=self)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    def __str__(self):
        return f'{self.name} : {self.user}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15)
    rank = models.ForeignKey(Rank, default=1, on_delete=models.PROTECT)

    @property
    def full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(user=self.user)

    @property
    def can_make_loan(self) -> bool:
        return self.rank.value >= settings.CUSTOMER_RANK_LOAN

    @property
    def default_account(self) -> Account:
        return Account.objects.filter(user=self.user).first()

    def __str__(self):
        return f'{self.full_name}'


class Transaction(models.Model):
    transaction_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    uid = models.ForeignKey(UID, on_delete=models.PROTECT)

    @classmethod
    def transfer(cls, amount, debit_account, debit_description, credit_account, credit_description, debit_type,
                 credit_type, is_loan):
        assert amount > 0, 'No negative amount allowed for transfer'
        with transaction.atomic():
            if debit_account.balance > amount or is_loan:
                uuid = UID.uid
                cls(amount=-amount, uid=uuid, account=debit_account, description=debit_description,
                    transaction_type=debit_type)
                cls(amount=amount, uid=uuid, account=credit_account, description=credit_description,
                    transaction_type=credit_type)
            else:
                # create own error here
                raise ValueError
        return uuid

    def __str__(self):
        return f'{self.amount} : {self.uid} : {self.date} : {self.account} : {self.transaction_type} : {self.description}'

