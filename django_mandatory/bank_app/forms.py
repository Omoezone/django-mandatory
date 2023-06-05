from django import forms
from django.contrib.auth.models import User
from .models import Customer, Account, TransferModel
from django.core.exceptions import ObjectDoesNotExist


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self._errors['username'] = self.error_class(['Username already exists.'])
        return self.cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username', disabled=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('rank', 'phone')


class NewAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('name',)


class TransferForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Debit Account', queryset=Customer.objects.none())
    debit_description = forms.CharField(label='Debit Account Text', max_length=25)
    credit_account = forms.IntegerField(label='Credit Account Number')
    credit_description = forms.CharField(label='Credit Account Text', max_length=25)

    def clean(self):
        super().clean()

        # Ensure credit account exist
        credit_account = self.cleaned_data.get('credit_account')
        try:
            Account.objects.get(pk=credit_account)
        except ObjectDoesNotExist:
            self._errors['credit_account'] = self.error_class(['Credit account does not exist.'])

        # Ensure positive amount
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data


class TransModelForm(forms.ModelForm):
    state = forms.BooleanField(label='Is last update', required=False)

    class Meta:
        model = TransferModel
        fields = ('amount', 'debit_account', 'debit_description', 'credit_account', 'credit_description')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('state'):
            instance.state = TransferModel.StateEnum.CREATED
        else:
            instance.state = TransferModel.StateEnum.PENDING
        if commit:
            instance.save()
        return instance

      
class SearchCustomers(forms.Form):
    search_query = forms.CharField(label="Search For Customer", max_length=40)
