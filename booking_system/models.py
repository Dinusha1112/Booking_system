from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    rewards_points = models.PositiveIntegerField(default=0)  # Add this line
    last_activity = models.DateTimeField(auto_now=True)  # Optional but useful

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def calculate_rewards(self):
        from movies.models import Booking
        bookings_count = Booking.objects.filter(user=self.user).count()
        self.rewards_points = bookings_count * 10  # 10 points per booking
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Promotion(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/')
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, null=True, blank=True)
    reward_name = models.CharField(max_length=100, default='Default Reward')
    reward_points = models.PositiveIntegerField(default=0)
    claimed_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=15, unique=True)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'reward_name')  # Prevent duplicate claims

    def __str__(self):
        return f"{self.user.username}'s {self.reward_name}"