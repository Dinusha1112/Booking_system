from django import forms
from .models import Booking, Seat, BookedSeat


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats']

    def __init__(self, *args, **kwargs):
        showtime = kwargs.pop('showtime', None)
        super().__init__(*args, **kwargs)
        if showtime and showtime.theater.screen_set.exists():
            screen = showtime.theater.screen_set.first()
            self.fields['seats'].queryset = Seat.objects.filter(
                screen=screen
            ).order_by('row', 'seat_number')