from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='theaters/')
    contact_number = models.CharField(max_length=15)
    screens = models.PositiveIntegerField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, help_text="Bootstrap icon class")

    def __str__(self):
        return self.name


class TheaterFacility(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('theater', 'facility')


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
        return f"Screen {self.screen_number} ({self.theater.name})"


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movies/images/')
    duration = models.DurationField()
    language = models.CharField(max_length=50)
    release_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.title


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, null=True, blank=True)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} at {self.time} on {self.date}"


class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    row = models.CharField(max_length=2)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.row}{self.seat_number}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat, through='BookedSeat')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    booking_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.showtime.movie.title}"


class BookedSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['booking', 'seat']]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'phone_number': '',
                'gender': ''
            }
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


def theaters_view(request):
    theaters = Theater.objects.all().prefetch_related(
        'theaterfacility_set__facility',
        'screen_set'
    ).order_by('name')

    return render(request, 'booking_system/theaters.html', {
        'theaters': theaters,
        'active_page': 'theaters'
    })