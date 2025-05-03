from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegisterForm, ContactForm, ProfileEditForm
from .models import Promotion, UserProfile
from movies.models import Movie, Theater, Booking


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
    profile = request.user.userprofile
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    # 10 points per booking
    profile.calculate_rewards()

    return render(request, 'booking_system/profile.html', {
        'profile': profile,
        'bookings': bookings,
        'bookings_count': bookings.count(),
        'rewards_points': profile.rewards_points,
        'rewards_progress': min(100, (profile.rewards_points % 100)),
        'rewards_needed': max(0, 100 - (profile.rewards_points % 100))
    })

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


@login_required
def profile_edit_view(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'booking_system/profile_edit.html', {
        'form': form,
        'profile': profile
    })