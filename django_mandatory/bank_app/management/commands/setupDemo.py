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
        transfer_in = Account.objects.create(user=bank_user, name='Bank transfer in')
        transfer_out = Account.objects.create(user=bank_user, name='Bank transfer out')
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
        Transaction.transfer(
            10_000_000,
            transfer_out,
            'Start Credit',
            transfer_in,
            'Start Credit',
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

        admin_user = User.objects.create_user('admin', email='admin@mail.dk', password='adgangskode')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'user'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_customer = Customer(user=admin_user, phone='88885555')
        admin_customer.save()
        admin_account = Account.objects.create(user=admin_user, name='Admin account')
        admin_account.save()

        Transaction.transfer(
            1_000,
            ops_account,
            'Payout to admin',
            admin_account,
            'Payout from bank'
        )


