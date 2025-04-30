from django.contrib import admin
from .models import Movie, Theater, Showtime, Booking


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_genres_display', 'release_date', 'language')
    list_filter = ('release_date', 'language')
    filter_horizontal = ('genres',)

    def get_genres_display(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    get_genres_display.short_description = 'Genres'


admin.site.register(Movie, MovieAdmin)
admin.site.register(Theater)
admin.site.register(Showtime)
admin.site.register(Booking)