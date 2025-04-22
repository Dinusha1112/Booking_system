from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomLoginForm

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    success_url = reverse_lazy('home')  # Change 'home' if your home view is named differently
from django.shortcuts import render

# Create your views here.
