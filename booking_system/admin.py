from django.contrib import admin
from .models import Movie
from .models import Booking
from .models import Register


from django.contrib.auth.models import User


admin.site.register(Movie)
admin.site.register(Booking)
admin.site.register(Register)