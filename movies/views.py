from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Movie, Theater, Showtime, Seat, Booking, BookedSeat
from .forms import BookingForm
from django.db import models


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

    # Get theaters where this movie is being shown
    movie_theaters = Theater.objects.filter(
        showtime__movie=showtime.movie,
        showtime__date__gte=timezone.now().date()
    ).distinct()

    # Rest remains exactly the same
    available_dates = Showtime.objects.filter(
        movie=showtime.movie
    ).dates('date', 'day').distinct()

    available_times = Showtime.objects.filter(
        movie=showtime.movie,
        date=showtime.date
    ).order_by('time').values_list('time', flat=True).distinct()

    if request.method == 'POST':
        form = BookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            # Create booking
            booking = Booking(
                user=request.user,
                showtime=showtime,
                total_price=showtime.price * len(form.cleaned_data['seats']),
                payment_status=True
            )
            booking.save()

            # Book the seats
            for seat in form.cleaned_data['seats']:
                seat.is_booked = True
                seat.save()
                BookedSeat.objects.create(booking=booking, seat=seat)

            return redirect('movies:booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm(showtime=showtime)

    return render(request, 'movies/booking.html', {
        'showtime': showtime,
        'movie_theaters': movie_theaters,
        'available_dates': available_dates,
        'available_times': available_times,
        'form': form
    })

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'movies/booking_confirmation.html', {
        'booking': booking
    })

