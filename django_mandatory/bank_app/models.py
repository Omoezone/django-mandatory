from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Customer(models.Model):
   user = models.ForeignKey(User, on_delete=(models.CASCADE))
   phone = models.CharField(max_length=15)
   rank = models.IntegerField(max_length=1)

class Employee(models.Model):
   user = models.ForeignKey(User, on_delete=(models.CASCADE))
   phone = models.CharField(max_length=15)

class Account(models.Model):
   number = models.IntegerField(max_length=10)
   balance = models.DecimalField(max_length=10, decimal_places=2)
   is_loan = models.BooleanField(default=False)
   customer = models.ForeignKey(Customer)
   # use a trigger when customer is deleted to prevent invalid customer id

class Transaction(models.Model):
   type = models.CharField(max_length=255)
   amount = models.DecimalField(max_length=10, decimal_places=2)
   description = models.CharField(max_length=255)
   date = models.DateTimeField(datetime.now)
   account = models.ForeignKey(Account)
   # use a trigger when account is deleted to prevent invalid account id
