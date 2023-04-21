from django.contrib import admin
from .models import UID, Customer, Account, Transaction, Rank

admin.site.register(UID)
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Rank)
