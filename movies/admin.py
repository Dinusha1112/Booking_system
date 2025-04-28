from django.contrib import admin
from .models import Movie, Showtime, Seat, Screen, Booking, BookedSeat

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 1

class ScreenAdmin(admin.ModelAdmin):
    inlines = [SeatInline]
    list_display = ('theater', 'screen_number', 'screen_type', 'capacity')
    list_filter = ('theater', 'screen_type')

class ShowtimeInline(admin.TabularInline):
    model = Showtime
    extra = 1

class MovieAdmin(admin.ModelAdmin):
    inlines = [ShowtimeInline]
    list_display = ('title', 'genre', 'release_date', 'rating')
    list_filter = ('genre', 'release_date')
    search_fields = ('title',)

class BookedSeatInline(admin.TabularInline):
    model = BookedSeat
    extra = 0

class BookingAdmin(admin.ModelAdmin):
    inlines = [BookedSeatInline]
    list_display = ('id', 'user', 'showtime', 'total_price', 'payment_status')
    list_filter = ('payment_status', 'showtime__theater')
    search_fields = ('user__username', 'showtime__movie__title')

admin.site.register(Movie, MovieAdmin)
admin.site.register(Showtime)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Seat)
admin.site.register(Booking, BookingAdmin)
admin.site.register(BookedSeat)