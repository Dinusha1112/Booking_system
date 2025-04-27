from django.contrib import admin
from .models import Movie, Showtime, Seat, Booking, BookedSeat

admin.site.register(Movie)
admin.site.register(Showtime)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(BookedSeat)

from django.contrib import admin
from .models import Theater, Facility, TheaterFacility, Screen

class FacilityInline(admin.TabularInline):
    model = TheaterFacility
    extra = 1

class ScreenInline(admin.TabularInline):
    model = Screen
    extra = 1

class ShowtimeInline(admin.TabularInline):
    model = Showtime
    extra = 1

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'contact_number')
    inlines = [FacilityInline, ScreenInline, ShowtimeInline]

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ('theater', 'screen_number', 'screen_type', 'capacity')
    list_filter = ('theater', 'screen_type')