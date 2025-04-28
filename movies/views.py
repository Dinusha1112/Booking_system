from django.shortcuts import render
from django.utils import timezone
from .models import Movie, Theater, Showtime


def movies_view(request):
    current_date = timezone.now().date()
    now_showing = Movie.objects.filter(release_date__lte=current_date)
    coming_soon = Movie.objects.filter(release_date__gt=current_date)

    theater_id = request.GET.get('theater')
    if theater_id:
        now_showing = now_showing.filter(showtime__theater_id=theater_id).distinct()

    return render(request, 'movies/movies.html', {
        'now_showing': now_showing,
        'coming_soon': coming_soon,
        'theaters': Theater.objects.all(),
        'selected_theater': int(theater_id) if theater_id else None
    })


def theaters_view(request):
    theaters = Theater.objects.all()
    return render(request, 'movies/theaters.html', {
        'theaters': theaters
    })