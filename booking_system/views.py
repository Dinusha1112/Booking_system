from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import BookingForm
from .models import Movie
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm

# ========================
# HOME VIEW
# ========================
def home(request):
    """
    Display a list of all movies on the home page.
    """
    movies = Movie.objects.all()  # Fetch all movies from DB
    return render(request, 'booking_system/home.html', {'movies': movies})


def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered successfully!")
            return redirect('home')
    return render(request, 'booking_system/register.html', {'form': form})


# ========================
# USER PROFILE VIEW
# ========================
@login_required
def profile_view(request):
    """
    Show the user's profile page.
    """
    return render(request, 'booking_system/profile.html')


# ========================
# BOOKING VIEW
# ========================
@login_required
def book_ticket(request, movie_id):
    """
    Handle booking form for a selected movie.
    """
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.movie = movie
            booking.save()
            return redirect('home')  # Redirect after successful booking
    else:
        form = BookingForm()

    return render(request, 'booking_system/book_ticket.html', {
        'form': form,
        'movie': movie
    })
