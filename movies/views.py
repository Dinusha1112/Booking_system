from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Showtime, Seat
from .forms import BookingForm


@login_required
def book_now(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)

    # Group seats by row for display
    seats = Seat.objects.all()
    seat_rows = {}
    for seat in seats:
        if seat.row not in seat_rows:
            seat_rows[seat.row] = []
        seat_rows[seat.row].append(seat)
    seat_rows = sorted(seat_rows.items())

    if request.method == 'POST':
        form = BookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.showtime = showtime
            booking.total_price = showtime.price * len(form.cleaned_data['seats'])
            booking.save()
            form.save_m2m()  # Save many-to-many relationship

            # Mark seats as booked
            for seat in booking.seats.all():
                seat.is_booked = True
                seat.save()

            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm(showtime=showtime)

    return render(request, 'booking_system/book_now.html', {
        'showtime': showtime,
        'seat_rows': seat_rows,
        'form': form,
    })

def home_view(request):
    movies = Movie.objects.all().prefetch_related('showtime_set')[:3]
    return render(request, 'booking_system/home.html', {'movies': movies})