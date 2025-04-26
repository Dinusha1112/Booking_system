from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from movies.models import Movie

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'booking_system/register.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next', 'profile')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'booking_system/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'booking_system/profile.html', {
        'profile': request.user.userprofile
    })

def home_view(request):
    movies = Movie.objects.all()[:3]  # Get first 3 movies for the homepage
    return render(request, 'booking_system/home.html', {'movies': movies})