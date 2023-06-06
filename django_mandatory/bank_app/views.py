from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, reverse
from .forms import NewUserForm, CustomerForm, UserForm, NewAccountForm, TransferForm, TransModelForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Account, Customer, Transaction, TransferModel
from django.db import IntegrityError
from secrets import token_urlsafe
from .errors import InsufficientFunds, NotAuthenticatedAPI, PostException, PutException, TransferError
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import time
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.authtoken.models import Token
from .serializers import TransferModelSerializer


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
                send_welcome_email(user)
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
    #assert request.user.is_staff, 'Customer user routing staff view.'

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
    assert not request.user.is_staff, 'Staff user routing customer view.'
    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            try:
                # midlertidig object der bliver brugt til kommunikation mellem bank a og bank B
                transModel = TransferModel.objects.create(
                    amount=request.POST.get("amount"),
                    debit_account=int(request.POST.get("debit_account")),
                    debit_description=request.POST.get("debit_description"),
                    credit_account=int(request.POST.get("credit_account")),
                    credit_description=request.POST.get("credit_description"),
                    idempotence=int(time.time()),
                )
                # This one is used if the external transfer is tested locally
                #user = User.objects.get(pk=request.user.pk)
                #token, created = Token.objects.get_or_create(user=user)
                # User authentication
                authResponse = requests.post("http://localhost:8001/api-token-auth/",
                                       data={"username": "admin", "password": "123"})
                tokenB = authResponse.json()
                transfer_serializer = TransferModelSerializer(transModel)
                serialized_data = transfer_serializer.data
                # Start transaction/communication with bank b
                response = requests.post(settings.EXTERNAL_BANK_URL, json=serialized_data, headers={'Authorization': f'Token {tokenB["token"]}',
                                                                       'Content-Type': 'application/json'})
                if response.status_code == 401:
                    raise NotAuthenticatedAPI
                return view_transfer_data(request, transModel.pk)
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
    return render(request, 'bank/send_transfer_request.html', context)


@login_required()
def view_transfer_data(request, pk):
    transModel = get_object_or_404(TransferModel, pk=pk)
    if request.method == 'GET':
        transfer_form = TransModelForm(instance=transModel)
    elif request.method == 'POST':
        transfer_form = TransModelForm(request.POST, instance=transModel)
        if transfer_form.is_valid():
            try:
                print("IT IS VALID")
                transfer_form.save()
                # This is used to get the API key for bank B
                authResponse = requests.post("http://localhost:8001/api-token-auth/",
                                             data={"username": "dummy", "password": "adgangskode"})
                tokenB = authResponse.json()
                transfer_serializer = TransferModelSerializer(transModel)
                serialized_data = transfer_serializer.data
                response = requests.put(settings.EXTERNAL_BANK_URL, json=serialized_data,
                                         headers={'Authorization': f'Token {tokenB["token"]}',
                                                  'Content-Type': 'application/json'})
                if response.status_code == 201:
                    # End of transaction / communication
                    amount = transModel.amount
                    debit_account = Account.objects.get(pk=transModel.debit_account)
                    debit_description = transModel.debit_description
                    credit_account = Account.objects.get(pk=4)
                    credit_description = transModel.credit_description
                    transfer = Transaction.transfer(amount, debit_account, debit_description, credit_account,
                                                    credit_description)
                    print(transfer)
                    # Cleanup, as it is not needed anymore
                    transModel.delete()
                    return customer_dashboard(request)
            except TransferError:
                transModel.delete()
                context = {
                    'title': 'Transfer Error',
                    'error': 'Problem happened when validating data.'
                }
                return render(request, 'bank/error.html', context)
    else:
        transfer_form = TransModelForm(instance=transModel)
    context = {
        "transModel": transModel,
        "transfer_form": transfer_form,
    }
    return render(request, 'bank/view_transfer_data.html', context)

# --- Bank B ---
@api_view(['POST', 'PUT'])
def receive_transfer(request):
    # Post is the first part, where the placeholder object is first created for bank b
    if request.method == 'POST':
        TransferSerializer = TransferModelSerializer(data=request.data)
        if TransferSerializer.is_valid():
            try:
                deserialized_data = TransferSerializer.data
                transfer_object = TransferModel(**deserialized_data)
                transfer_object.state = TransferModel.StateEnum.PENDING
                transfer_object.save()
                print("transfer_object data is: ", transfer_object)
                return Response("Transaction initialized", status=200)
            except:
                # No reason to render error page, as this is only via HTTP/API
                transfer_object.delete()
                raise PostException
        else:
            return Response("Unable to validate serializer data", status=400)
    elif request.method == 'PUT':
        TransferSerializer = TransferModelSerializer(data=request.data)
        if TransferSerializer.is_valid():
            try:
                deserialized_data = TransferSerializer.data
                print("DESERIALISED DATA: ", deserialized_data)
                transfer_object = get_object_or_404(TransferModel, idempotence=deserialized_data["idempotence"])
                print("Transfer_object in Bank B", transfer_object)
                if deserialized_data.get("state") == TransferModel.StateEnum.PENDING.value:
                    print("PENDING PUT")
                    transfer_object.amount = deserialized_data["amount"]
                    transfer_object.debit_account = deserialized_data["debit_account"]
                    transfer_object.debit_description = deserialized_data["debit_description"]
                    transfer_object.credit_account = deserialized_data["credit_account"]
                    transfer_object.credit_description = deserialized_data["credit_description"]
                    transfer_object.state = deserialized_data["state"]
                    transfer_object.save()
                    return Response("Transaction updated", status=204)
                elif deserialized_data.get("state") == TransferModel.StateEnum.CREATED.value:
                    print("ENTERED CREATED STATE")
                    amount = Decimal(deserialized_data.get("amount"))
                    debit_account = Account.objects.get(pk=3)
                    debit_description = deserialized_data.get("debit_description")
                    credit_account = Account.objects.get(pk=int(deserialized_data.get("debit_account")))
                    credit_description = deserialized_data.get("credit_description")
                    print(amount, debit_account, debit_description, credit_account, credit_description)
                    print(type(amount), type(debit_account), type(debit_description), type(credit_account), type(credit_description))

                    transaction_transfer = Transaction.transfer(amount, debit_account, debit_description, credit_account, credit_description)
                    print("TRANSACTION BANK B", transaction_transfer)
                    transfer_object.state = TransferModel.StateEnum.CREATED
                    transfer_object.save()
                    return Response("Transaction Completed", status=201)
            except:
                # No reason to render error page, as this is only via HTTP/API
                transfer_object.delete()
                raise PutException
    else:
        return Response("error with reqeust method", status=405)
