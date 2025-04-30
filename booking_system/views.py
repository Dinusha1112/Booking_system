from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegisterForm, ContactForm
from .models import Promotion
from movies.models import Movie, Theater


def home_view(request):
    now_showing = Movie.objects.filter(
        showtime__date__gte=timezone.now().date()
    ).distinct().order_by('title')[:8]

    upcoming_movies = Movie.objects.filter(
        release_date__gt=timezone.now().date()
    ).order_by('release_date')[:4]

    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )[:3]

    return render(request, 'booking_system/home.html', {
        'now_showing': now_showing,
        'upcoming_movies': upcoming_movies,
        'promotions': promotions
    })

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'booking_system/contact.html', {'form': form})


def offers_view(request):
    promotions = Promotion.objects.filter(is_active=True)
    return render(request, 'booking_system/offers.html', {'promotions': promotions})


@login_required
def profile_view(request):
    user_profile = request.user.userprofile
    return render(request, 'booking_system/profile.html', {'profile': user_profile})


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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'booking_system/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')