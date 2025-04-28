from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.movies_view, name='movies'),
    path('theaters/', views.theaters_view, name='theaters'),
]