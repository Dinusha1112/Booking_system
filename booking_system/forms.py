from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'gender', 'password1','password2']