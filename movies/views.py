from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Movie, Theater, Showtime, Seat, Booking, BookedSeat
from .forms import BookingForm


def movies_view(request):
    current_date = timezone.now().date()
    movies = Movie.objects.all()

    # Apply filters
    if request.GET.get('q'):
        movies = movies.filter(title__icontains=request.GET['q'])

    if request.GET.getlist('genres'):
        movies = movies.filter(genres__name__in=request.GET.getlist('genres')).distinct()

    if request.GET.get('theater'):
        movies = movies.filter(showtime__theater_id=request.GET['theater']).distinct()

    # Split into now showing and coming soon
    now_showing = movies.filter(release_date__lte=current_date)
    coming_soon = movies.filter(release_date__gt=current_date)

    context = {
        'now_showing': now_showing,
        'coming_soon': coming_soon,
        'theaters': Theater.objects.all(),
        'GENRE_CHOICES': Movie.GENRE_CHOICES,
        'selected_genres': request.GET.getlist('genres'),
        'selected_theater': request.GET.get('theater'),
        'search_query': request.GET.get('q', '')
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
        'form': form
    })

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'movies/booking_confirmation.html', {
        'booking': booking
    })

