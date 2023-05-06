from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Customer, Account
# Create your views here.


@login_required
def index(request):
    # Use this bit to authenticate between users and admins
    if request.user.is_staff:
        return HttpResponseRedirect('staff_dashboard')
    else:
        return HttpResponseRedirect('customer_dashboard')
    # Which will decide which dashboard to show
    # return HttpResponseRedirect('customer_dashboard')


@login_required
def staff_dashboard(request):
    userList = User.objects.all()
    context = {
        'users': userList
    }
    return render(request, 'staff_dashboard.html', context)


@login_required
def customer_dashboard(request):
    accountList = Account.objects.all()
    context = {
        'accounts': accountList
    }
    return render(request, 'customer_dashboard.html', context)


@login_required
def customer_transaction(request):
    return render(request, 'customer_transaction.html')


@login_required
def customer_account(request):
    return render(request, 'customer_account.html')

def account_single(request, pk):
    account = get_object_or_404(Account, user=request.user, pk=pk)
    context = {
        'account': account,
    }

    return render(request, 'account_single.html', context)