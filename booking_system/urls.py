from django.urls import path
from . import views

urlpatterns = [
    # Home page - showing list of movies
    path('', views.home, name='home'),



    # User profile
    path('profile/', views.profile_view, name='profile'),

    # Booking a ticket for a movie
    path('book/<int:movie_id>/', views.book_ticket, name='book_ticket'),
    path('register/', views.register_view, name='register'),
]
