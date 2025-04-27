from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('book/<int:showtime_id>/', views.book_now, name='book_now'),
    path('', views.movies_view, name='movies'),
]