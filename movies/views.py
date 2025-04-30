from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Movie, Theater, Showtime, Seat, Booking, BookedSeat
from .forms import BookingForm

def movies_view(request):
    current_date = timezone.now().date()
    now_showing = Movie.objects.filter(release_date__lte=current_date)
    coming_soon = Movie.objects.filter(release_date__gt=current_date)

    theater_id = request.GET.get('theater')
    selected_theater_name = None

    if theater_id:
        now_showing = now_showing.filter(showtime__theater_id=theater_id).distinct()
        try:
            selected_theater_name = Theater.objects.get(id=theater_id).name
        except Theater.DoesNotExist:
            pass

    return render(request, 'movies/movies.html', {
        'now_showing': now_showing,
        'coming_soon': coming_soon,
        'theaters': Theater.objects.all(),
        'selected_theater': int(theater_id) if theater_id else None,
        'selected_theater_name': selected_theater_name
    })

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
            booking = Booking(
                user=request.user,
                showtime=showtime,
                total_price=showtime.price * len(form.cleaned_data['seats']),
                payment_status=True
            )
            booking.save()

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