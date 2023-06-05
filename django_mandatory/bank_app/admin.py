from django.contrib import admin
from .models import UID, Customer, Account, Transaction, Rank, TransferModel

admin.site.register(UID)
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Rank)
admin.site.register(TransferModel)
