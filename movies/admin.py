from django.contrib import admin
from .models import Movie, Showtime, Seat, Booking, BookedSeat

admin.site.register(Movie)
admin.site.register(Showtime)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(BookedSeat)