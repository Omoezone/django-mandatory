from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, reverse
from .forms import NewUserForm, CustomerForm, UserForm, NewAccountForm, TransferForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Account, Customer, Transaction
from django.db import IntegrityError
from secrets import token_urlsafe
from .errors import InsufficientFunds
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.core.mail import send_mail
from .serializers import b2bSerializer


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
                emailRes = send_welcome_email(user) #This works, but it needs proper allowance for outlook
                print("Email sent: ", emailRes)
                # Or proper setup of development SMTP server
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


def send_welcome_email(user):
    subject = f'Welcome to kea bank {user.username}'
    message = 'Welcome to kea bank.\n\nThank you for joining.\nAn account has automaticly been made for you.' \
              '\nRegards from KEA Bank'
    from_email = 'KeaBank@Bank.dk'
    to_email = [user.email]
    return send_mail(subject, message, from_email, to_email, fail_silently=False)

@login_required
def staff_customer_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'GET':
        user_form = UserForm(instance=customer.user)
        customer_form = CustomerForm(instance=customer)
    elif request.method == 'POST':
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
def staff_all_customers(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customers =  Customer.objects.select_related('user').all()[:10]

    context = {
        'customers' : customers
    }

    return render(request, 'bank/all_customers.html', context)

from django.db.models.functions import Lower
@login_required
def search_customers(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    search_query = request.GET.get('search_query')
    
    if not search_query:
        search_query = ''

    users = User.objects.filter(username__contains=search_query).filter(email__contains=search_query)

    context = {
        'users' : users,
        'search_query' : search_query
    }

    return render(request, 'bank/search_customers.html', context)


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
        print(request.POST)
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


# ------ FOREIGN TRANSFER ----  --

# --- Bank A ---
def send_transfer_request(request):
    # assert not data.user.is_staff, 'Staff user routing customer view.'
    url = 'http://localhost:8001/api/receive_transfer/'
    # Get data cleaned from frontend
    if request.method == 'POST':
        reqData = request.POST
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            # Look into setting the reciever
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_description = form.cleaned_data['debit_description']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
            credit_description = form.cleaned_data['credit_description']
            try:
                transfer = Transaction.transfer(amount, debit_account, debit_description, credit_account,credit_description)
                payload = {
                    "amount": reqData.get("amount"),
                    "d_account": reqData.get("debit_account"),
                    "d_description": reqData.get("debit_description")
                }
                # User authentication'
                credentials = {
                    'username': 'dummy',
                    'password': 'adgangskode'
                }
                tokenRes = requests.post('http://localhost:8001/api-token-auth/', data=credentials)
                token = tokenRes.json().get("token")

                # Send data to bank b
                print("BEFORE REQUEST TO BANK B")
                response = requests.post(url, json=payload,
                                         headers={
                                            'Authorization': f'Token {token}',
                                            'Content-Type': 'application/json'})
                print("RESPONSE from forst request ", response)
                # Receive token from bank b

                return transaction_details(request, transfer)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer Error',
                    'error': 'Insufficient funds for transfer.'
                }
                return render(request, 'bank/error.html', context)
        # Temp error handling
        else:
            context = {
                'title': 'Form Error',
                'error': 'Unable to clean the formdata, please try again'
            }
            return render(request, 'bank/error.html', context)
    else:
        form = TransferForm()
        form.fields['debit_account'].queryset = request.user.customer.accounts
        context = {
            'form': form,
        }
    return render(request, 'bank/send_transfer_request.html', context)


# --- Bank B ---
@api_view(['POST'])
def receive_transfer(request):
    # Get data from bank a
    if request.method == 'POST':
        TransferSerializer = b2bSerializer(data=request.data)
        if TransferSerializer.is_valid():
            deserialized_data = TransferSerializer.data

            # Access individual field values
            amount = deserialized_data['amount']
            c_account = Account.objects.get(pk=3)  # Here we ask to always get id 3, as that is the bank: incoming transfer account
            c_description = f"Money Recieved from external ID: {deserialized_data['d_account']}"
            d_account = Account.objects.get(pk=deserialized_data['d_account'])
            d_description = deserialized_data['d_description']



            # Process the transfer and create the transfer object
            transfer = Transaction.transfer(amount, c_account, c_description, d_account, d_description)
            print("made transfer in bank b", transfer)

            # Clear the session data

            return Response("Transaction completed", status=201)
        else:
            return Response("Error with creation of transaction", status=409)
        # Return the token as a response
        return Response("Token from bank b", token)
    else:
        return Response("not post", status=405)


@login_required
def foreign_transfer_details(request, pk):
    pass