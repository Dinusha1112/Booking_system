from django import forms
from .models import Booking, Seat

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats']

    def __init__(self, *args, **kwargs):
        showtime = kwargs.pop('showtime', None)
        super().__init__(*args, **kwargs)
        if showtime:
            self.fields['seats'].queryset = Seat.objects.filter(is_booked=False)