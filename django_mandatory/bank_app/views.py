from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.


@login_required
def index(request):
    # Use this bit to authenticate between users and admins
    # Which will decide which dashboard to show
    return HttpResponseRedirect('customer_dashboard')


@login_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

