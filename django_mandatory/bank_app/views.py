
import requests
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, reverse
from .forms import NewUserForm, CustomerForm, UserForm, NewAccountForm, TransferForm, FtForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Account, Customer, Transaction
from django.db import IntegrityError, transaction
from secrets import token_urlsafe
from .errors import InsufficientFunds



@login_required
def index(request):
    return HttpResponseRedirect('customer_dashboard')


@login_required
def customer_dashboard(request):
    accounts = request.user.customer.accounts
    context = {
        'accounts': accounts,
    }

    return render(request, 'bank/customer_dashboard.html', context)


@login_required
def staff_new_customer(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_user_form = NewUserForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if new_user_form.is_valid() and customer_form.is_valid():
            username = new_user_form.cleaned_data['username']
            first_name = new_user_form.cleaned_data['first_name']
            last_name = new_user_form.cleaned_data['last_name']
            email = new_user_form.cleaned_data['email']
            password = token_urlsafe(16)
            rank = customer_form.cleaned_data['rank']
            phone = customer_form.cleaned_data['phone']
            try:
                user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                )
                print(f'********** Username: {username} -- Password: {password}')
                Customer.objects.create(user=user, rank=rank, phone=phone)
                print("User.pk after creation ", user.pk)
                return staff_customer_details(request, user.pk)
            except IntegrityError:
                context = {
                    'title': 'Database Error',
                    'error': 'User could not be created.'
                }
                return render(request, '/', context)
    else:
        new_user_form = NewUserForm()
        customer_form = CustomerForm()
    context = {
        'new_user_form': new_user_form,
        'customer_form': customer_form,
    }
    return render(request, 'bank/staff_new_customer.html', context)


@login_required
def staff_customer_details(request, pk):
    print("Entered staff_customer_details", request, pk)
    assert request.user.is_staff, 'Customer user routing staff view.'
    customer = get_object_or_404(Customer, pk=pk)
    print("customer", customer)
    if request.method == 'GET':
        print("entered get")
        user_form = UserForm(instance=customer.user)
        customer_form = CustomerForm(instance=customer)
    elif request.method == 'POST':
        print("entered post")
        user_form = UserForm(request.POST, instance=customer.user)
        customer_form = CustomerForm(request.POST, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
    new_account_form = NewAccountForm()
    context = {
        'customer': customer,
        'user_form': user_form,
        'customer_form': customer_form,
        'new_account_form': new_account_form,
    }
    return render(request, 'bank/staff_customer_details.html', context)


@login_required
def staff_new_account_partial(request, user):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_account_form = NewAccountForm(request.POST)
        if new_account_form.is_valid():
            Account.objects.create(user=User.objects.get(pk=user), name=new_account_form.cleaned_data['name'])
    return HttpResponseRedirect(reverse('bank_app:staff_customer_details', args=(user,)))


@login_required
def staff_account_list_partial(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    accounts = customer.accounts
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank/staff_account_list_partial.html', context)


@login_required
def staff_account_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    account = get_object_or_404(Account, pk=pk)
    context = {
        'account': account,
    }
    return render(request, 'bank/account_details.html', context)


@login_required
def transaction_details(request, transaction):
    movements = Transaction.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    context = {
        'movements': movements,
    }
    return render(request, 'bank/transaction_details.html', context)


@login_required
def account_details(request, pk):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    account = get_object_or_404(Account, user=request.user, pk=pk)
    context = {
        'account': account,
    }
    print(context)
    return render(request, 'bank/account_details.html', context)


@login_required
def customer_account(request):
    return render(request, 'bank/customer_account.html')


@login_required
def make_transfer(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_description = form.cleaned_data['debit_description']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
            credit_description = form.cleaned_data['credit_description']
            try:
                transfer = Transaction.transfer(amount, debit_account, debit_description,
                                                credit_account, credit_description)
                return transaction_details(request, transfer)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer Error',
                    'error': 'Insufficient funds for transfer.'
                }
                return render(request, 'bank/error.html', context)
    else:
        form = TransferForm()
        form.fields['debit_account'].queryset = request.user.customer.accounts
        context = {
            'form': form,
        }
    return render(request, 'bank/make_transfer.html', context)


@login_required
def transaction_details(request, transaction):
    movements = Transaction.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    context = {
        'movements': movements,
    }
    return render(request, 'bank/transaction_details.html', context)


@login_required
def make_loan(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    if not request.user.customer.can_make_loan:
        context = {
            'title': 'Create Loan Error',
            'error': 'Loan could not be completed.'
        }
        return render(request, 'bank/error.html', context)
    if request.method == 'POST':
        request.user.customer.make_loan(Decimal(request.POST['amount']), request.POST['name'])
        return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))
    return render(request, 'bank/make_loan.html', {})

@login_required()
@transaction.atomic()
def transfer_foreign(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'
    # LAD DEN TAGE DEFAULT URL
    url = 'http://localhost:8000/get_transfer_foreign/'
    username = "admin"
    password = "adgangskode"

    # Create Transaction for bank 1.
    try:
        if request.method == 'POST':
            form = FtForm(request.POST, initial={"credit_account": 3})
            if form.is_valid():
                amount = form.cleaned_data['amount']
                debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'])
                debit_description = form.cleaned_data['debit_description']
                credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
                credit_description = form.cleaned_data['credit_description']
            try:
                print(amount, debit_account, debit_description, credit_account, credit_description)
                transfer = Transaction.transfer(amount, debit_account, debit_description, credit_account, credit_description)
                print("transfer id", transfer)

                data = {"id": transfer, "amount": amount, "debit_account": debit_account}
                response = requests.post(url, data, auth=(username, password))
                if response.status_code == 200:
                    print("it works")
                else:
                    print("error with requests post: ", response.status_code)

                print("response in method", response.content)
                return transaction_details(request, transfer)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer Error',
                    'error': 'Insufficient funds for transfer.'
                }
                return render(request, 'bank/error.html', context)
        else:
            form = FtForm(initial={"credit_account": 3})
            context = {
                'form': form,
            }
            print("context", context)
            return render(request, 'bank/transfer_foreign.html', context)

    except IntegrityError:
        print("ERROR HAPPENED IN FOREIGN TRANSFER")
        pass
    # Make the debit account in the request the account that sends money
    # Make the credit account in the request the bank account

    # step 1 lav en transfer for bank a

    # step 2 send post to bank b ud fra transfer fra step 1,
    #   der siger at du gerne vil lave en transaction

    # step 3 bank b saves post data and send a confirm token to bank a. It sets itself in a reserved state

    # step 4 bank a recieves confirm token and checks for any changes

    # step 4.1 if any changes, send a put or patch to bank b with changed data
    # step 4.2 bank b recieves and updates its data from post requests earlier and send confirm token back
    # Repeat until no changes or second trigger (not thought of yet)

    # step 5 bank b, creates the transaction and send a confirmation to bank a




    # If success create one for bank 2.
    # Make the debit account in the request be the bank
    # Make the credit be the account we want to send to


    # Handle errors with roolback()
        # Eventually call this method again, but with PUT or DELETE that does the opposite
    pass


@login_required()
@api_view(['POST', 'PUT', 'DELETE'])
@transaction.atomic()
def get_transfer_foreign(request):
    print("HELLO MATE FROM GETTAR")
    # Does the creation of transfer
    if request.method == 'POST':
        print("-------- RECIEVED POST REQUEST FROM BANK1 _------")
        # Does the update/change of created transfer
        return "1235325"
    elif request.method == 'PUT':
        pass
    # Delete the transfer for potential reset
    elif request.method == 'DELETE':
        pass
