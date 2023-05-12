from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Account, Transaction, Customer


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding demo data ...')

        bank_user = User.objects.create_user('bank', email='bank@mail.dk', password='adgangskode')
        bank_user.is_active = False
        bank_user.save()
        ipo_account = Account.objects.create(user=bank_user, name='Bank IPO Account')
        ops_account = Account.objects.create(user=bank_user, name='Bank OPS Account')
        bank_customer = Customer(user=bank_user, phone='555666')
        bank_customer.save()
        Transaction.transfer(
            10_000_000,
            ipo_account,
            'Operational Credit',
            ops_account,
            'Operational Credit',
            is_loan=True
        )

        dummy_user = User.objects.create_user('dummy', email='dummy@dummy.com', password='adgangskode')
        dummy_user.first_name = 'Dummy'
        dummy_user.last_name = 'Dimwit'
        dummy_user.save()
        dummy_customer = Customer(user=dummy_user, phone='555666')
        dummy_customer.save()
        dummy_account = Account.objects.create(user=dummy_user, name='Checking account')
        dummy_account.save()

        Transaction.transfer(
            1_000,
            ops_account,
            'Payout to dummy',
            dummy_account,
            'Payout from bank'
        )


