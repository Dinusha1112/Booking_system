from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Movie, Theater, Showtime, Seat, Booking, BookedSeat
from .forms import BookingForm
from django.db import models
from django.contrib import messages

def movies_view(request):
    current_date = timezone.now().date()

    # Base query for now showing (must have showtimes)
    now_showing = Movie.objects.filter(
        release_date__lte=current_date,
        showtime__date__gte=current_date
    ).distinct()

    # Base query for coming soon (don't require showtimes)
    coming_soon = Movie.objects.filter(
        release_date__gt=current_date
    ).distinct()

    # Apply filters to now showing
    search_query = request.GET.get('q', '')
    if search_query:
        now_showing = now_showing.filter(title__icontains=search_query)
        coming_soon = coming_soon.filter(title__icontains=search_query)

    selected_genres = request.GET.getlist('genres')
    if selected_genres:
        for genre in selected_genres:
            now_showing = now_showing.filter(genres__name=genre)
            coming_soon = coming_soon.filter(genres__name=genre)
        now_showing = now_showing.distinct()
        coming_soon = coming_soon.distinct()

    selected_theater = request.GET.get('theater')
    if selected_theater:
        now_showing = now_showing.filter(showtime__theater_id=selected_theater).distinct()
        # Don't filter coming_soon by theater as they may not have showtimes

    # Prefetch showtimes for now showing only
    now_showing = now_showing.prefetch_related(
        models.Prefetch(
            'showtime_set',
            queryset=Showtime.objects.filter(date__gte=current_date).order_by('date', 'time'),
            to_attr='current_showtimes'
        )
    )

    context = {
        'now_showing': now_showing,
        'coming_soon': coming_soon,
        'theaters': Theater.objects.all(),
        'GENRE_CHOICES': Movie.GENRE_CHOICES,
        'selected_genres': selected_genres,
        'selected_theater': selected_theater,
        'search_query': search_query,
        'current_date': current_date
    }
    return render(request, 'movies/movies.html', context)

def theaters_view(request):
    theaters = Theater.objects.all()
    return render(request, 'movies/theaters.html', {
        'theaters': theaters
    })

@login_required
def booking_view(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)

    # Get theaters showing this movie with upcoming showtimes
    movie_theaters = Theater.objects.filter(
        showtime__movie=showtime.movie,
        showtime__date__gte=timezone.now().date()
    ).distinct()

    # Get available dates for the CURRENT THEATER
    available_dates = Showtime.objects.filter(
        movie=showtime.movie,
        theater=showtime.theater,
        date__gte=timezone.now().date()
    ).dates('date', 'day').distinct()

    # Get available times for the CURRENT DATE
    available_times = Showtime.objects.filter(
        movie=showtime.movie,
        theater=showtime.theater,
        date=showtime.date
    ).order_by('time').values_list('time', flat=True).distinct()

    # Get screen for current showtime
    screen = showtime.theater.screen_set.first()
    if not screen:
        messages.error(request, "No screen configuration found for this theater")
        return redirect('movies:movies')

    # Get all booked seat IDs for THIS SPECIFIC showtime only
    booked_seat_ids = BookedSeat.objects.filter(
        booking__showtime=showtime,
        booking__is_cancelled=False
    ).values_list('seat_id', flat=True)

    if request.method == 'POST':
        form = BookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            selected_seats = form.cleaned_data['seats']

            # Validate no selected seats are already booked
            conflict_seats = [seat for seat in selected_seats if seat.id in booked_seat_ids]
            if conflict_seats:
                messages.error(request, f"Seat(s) {', '.join(str(seat) for seat in conflict_seats)} are already booked")
                return redirect('movies:booking', showtime_id=showtime_id)

            # Create booking
            booking = Booking(
                user=request.user,
                showtime=showtime,
                total_price=showtime.price * len(selected_seats),
                payment_status=True
            )
            booking.save()

            # Create BookedSeat records
            for seat in selected_seats:
                BookedSeat.objects.create(booking=booking, seat=seat)
                seat.is_booked = True
                seat.save()

            # Update rewards
            profile = request.user.userprofile
            profile.rewards_points += 10 * len(selected_seats)
            profile.save()

            return redirect('movies:booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm(showtime=showtime)

    return render(request, 'movies/booking.html', {
        'showtime': showtime,
        'movie_theaters': movie_theaters,
        'available_dates': available_dates,
        'available_times': available_times,
        'form': form,
        'booked_seat_ids': list(booked_seat_ids),
        'screen': screen  # Pass screen to template
    })

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'movies/booking_confirmation.html', {
        'booking': booking
    })


def find_showtime(request):
    movie_id = request.GET.get('movie_id')
    theater_id = request.GET.get('theater')
    date = request.GET.get('date')
    time = request.GET.get('time')

    try:
        showtime = Showtime.objects.get(
            movie_id=movie_id,
            theater_id=theater_id,
            date=date,
            time=time
        )
        return redirect('movies:booking', showtime_id=showtime.id)
    except (Showtime.DoesNotExist, ValueError):
        messages.error(request, "Selected showtime not available")
        # Try to find any available showtime for the same movie and theater
        available_showtime = Showtime.objects.filter(
            movie_id=movie_id,
            theater_id=theater_id,
            date__gte=timezone.now().date()
        ).order_by('date', 'time').first()

        if available_showtime:
            return redirect('movies:booking', showtime_id=available_showtime.id)
        return redirect('movies:movies')