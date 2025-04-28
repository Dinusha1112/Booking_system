from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    contact = models.CharField(max_length=15)
    image = models.ImageField(upload_to='theaters/')

    def __str__(self):
        return self.name


class Movie(models.Model):
    GENRE_CHOICES = [
        ('AC', 'Action'),
        ('CO', 'Comedy'),
        ('DR', 'Drama'),
        ('HO', 'Horror'),
        ('SF', 'Sci-Fi'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField()  # in minutes
    genre = models.CharField(max_length=2, choices=GENRE_CHOICES, null = True)
    release_date = models.DateField()
    poster = models.ImageField(upload_to='movies/')
    rating = models.FloatField(default=0.0)
    theaters = models.ManyToManyField(Theater, through='Showtime')

    def __str__(self):
        return self.title


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.movie.title} at {self.theater.name} - {self.date} {self.time}"


class Seat(models.Model):
    screen = models.ForeignKey('Screen', on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    row = models.CharField(max_length=2)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('screen', 'row', 'seat_number')

    def __str__(self):
        return f"{self.row}{self.seat_number} (Screen {self.screen.screen_number})"


class Screen(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    screen_number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    screen_type = models.CharField(max_length=20, choices=[
        ('standard', 'Standard'),
        ('imax', 'IMAX'),
        ('4dx', '4DX'),
        ('dolby', 'Dolby Cinema')
    ])

    class Meta:
        unique_together = ('theater', 'screen_number')

    def __str__(self):
        return f"Screen {self.screen_number} at {self.theater.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat, through='BookedSeat')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking #{self.id} for {self.showtime.movie.title}"


class BookedSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking', 'seat')

    def __str__(self):
        return f"{self.seat} in booking #{self.booking.id}"