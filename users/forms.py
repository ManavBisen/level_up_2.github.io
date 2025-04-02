from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Transaction

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class TransactionForm(forms.ModelForm):
    receiver_username = forms.CharField(max_length=150, help_text="Enter the username of the person you want to send XP to")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Enter your password to confirm the transaction")

    class Meta:
        model = Transaction
        fields = ['amount']
        
    def clean_receiver_username(self):
        username = self.cleaned_data.get('receiver_username')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("This user does not exist.")
        return username
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount

class UserSearchForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
