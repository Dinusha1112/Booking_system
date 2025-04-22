
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomLoginForm, CustomUserCreationForm
from django.views.generic import CreateView

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    success_url = reverse_lazy('home')  # Change to your real home if needed

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

