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
from .errors import InsufficientFunds, NotAuthenticatedAPI, PostException, PutException
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import time
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
    # Get data cleaned from frontend
    if request.method == 'POST':
        reqData = request.POST
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_description = form.cleaned_data['debit_description']
            credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
            credit_description = form.cleaned_data['credit_description']
            try:
                transfer = Transaction.transfer(amount, debit_account, debit_description, credit_account, credit_description)
                print(transfer)
                # midlertidig object der bliver brugt til kommunikation mellem bank a og bank B
                transModel = TransferModel.objects.create(
                    amount=request.POST.get("amount"),
                    debit_account=int(request.POST.get("debit_account")),
                    debit_description=request.POST.get("debit_description"),
                    credit_account=int(request.POST.get("credit_account")),
                    credit_description=request.POST.get("credit_description"),
                    idempotence=int(time.time()),
                )

                # User authentication
                # Dette bliver brugt til at få auth api key
                user = User.objects.get(pk=request.user.pk)
                token, created = Token.objects.get_or_create(user=user)
                authResponse = requests.post("http://localhost:8001/api-token-auth/",
                                       data={"username": "dummy", "password": "adgangskode"})
                tokenB = authResponse.json()
                print("token from bank b", tokenB["token"])

                transfer_serializer = TransferModelSerializer(transModel)
                serialized_data = transfer_serializer.data
                print("SERIALIZED DATA POST", serialized_data)

                # Send data to bank b
                response = requests.post(settings.EXTERNAL_BANK_URL, json=serialized_data, headers={'Authorization': f'Token {tokenB["token"]}',
                                                                       'Content-Type': 'application/json'})
                if response.status_code == 401:
                    raise NotAuthenticatedAPI

                print("RESPONSE from first request ", response)
                return view_transfer_data(request, transModel.pk)
            except InsufficientFunds:
                context = {
                    'title': 'Transfer Error',
                    'error': 'Insufficient funds for transfer.'
                }
                return render(request, 'bank/error.html', context)
        # Temp error handling HUSK AT FJERNE TIL SIDST
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


@login_required()
def view_transfer_data(request, pk):
    # Får fat i det object der blev lavet tidligere
    transModel = get_object_or_404(TransferModel, pk=pk)
    print("transmodel: ", transModel)
    if request.method == 'GET':
        # instance=transModel er måden form ved hvilke object den arbejder med
        transfer_form = TransModelForm(instance=transModel)
    elif request.method == 'POST':
        # make put request
        transfer_form = TransModelForm(request.POST, instance=transModel)
        if transfer_form.is_valid():
            print("IT IS VALID")
            transfer_form.save()
            authResponse = requests.post("http://localhost:8001/api-token-auth/",
                                         data={"username": "dummy", "password": "adgangskode"})
            tokenB = authResponse.json()
            print("REQUEST DATA FOR PUT ", request.POST)
            transfer_serializer = TransferModelSerializer(transModel)
            serialized_data = transfer_serializer.data
            print("SERIALIZED DATA PUT", serialized_data)

            response = requests.put(settings.EXTERNAL_BANK_URL, json=serialized_data,
                                     headers={'Authorization': f'Token {tokenB["token"]}',
                                              'Content-Type': 'application/json'})
            print("RES: ", response)
            if response.status_code == 201:
                print("ENTERED PUT END")
                return customer_dashboard(request)
    else:
        transfer_form = TransModelForm(instance=transModel)
    context = {
        "transModel": transModel,
        "transfer_form": transfer_form,
    }
    return render(request, 'bank/view_transfer_data.html', context)

# --- Bank B ---
# DETTE ER IKKE DENS NUVÆRENDE KORREKTE STADIE! TAG ALT MED ET GRAM SALT


@api_view(['POST', 'PUT'])
def receive_transfer(request):
    # Get data from bank a
    print(request.data)
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
                # Look into changing this
                raise PostException
        else:
            return Response("Unable to validate serializer data", status=400)
    elif request.method == 'PUT':
        TransferSerializer = TransferModelSerializer(data=request.data)
        if TransferSerializer.is_valid():
            try:
                deserialized_data = TransferSerializer.data
                transfer_object = get_object_or_404(TransferModel, idempotence=deserialized_data["idempotence"])
                if transfer_object.state == TransferModel.StateEnum.PENDING:
                    print("PENDING PUT")
                    transfer_object.save()
                    return Response("Transaction updated", status=204)
                elif transfer_object.state == TransferModel.StateEnum.CREATED:
                    print("ENTERED CREATED STATE")
                    transaction_transfer = Transaction.transfer(transfer_object.amount, transfer_object.credit_account, transfer_object.credit_description, transfer_object.debit_account, transfer_object.debit_description)
                    print("TRANSACTION BANK B", transaction_transfer)
                    return Response("Transaction Completed", status=201)
            except:
                raise PutException
    else:
        return Response("error with reqeust method", status=405)