from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.movies_view, name='movies'),
    path('theaters/', views.theaters_view, name='theaters'),
    path('book/<int:showtime_id>/', views.booking_view, name='booking'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]