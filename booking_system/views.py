from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .forms import UserRegisterForm, ContactForm, ProfileEditForm
from .models import Promotion, UserProfile, Reward, UserReward
from movies.models import Movie, Theater, Booking
import random
import string

def home_view(request):
    now_showing = Movie.objects.filter(
        showtime__date__gte=timezone.now().date()
    ).distinct().order_by('title')[:8]

    upcoming_movies = Movie.objects.filter(
        release_date__gt=timezone.now().date()
    ).order_by('release_date')[:4]

    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )[:3]

    return render(request, 'booking_system/home.html', {
        'now_showing': now_showing,
        'upcoming_movies': upcoming_movies,
        'promotions': promotions
    })

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'booking_system/contact.html', {'form': form})


def offers_view(request):
    promotions = Promotion.objects.filter(is_active=True)
    return render(request, 'booking_system/offers.html', {'promotions': promotions})


@login_required
def profile_view(request):
    profile = request.user.userprofile
    current_date = timezone.now().date()

    # Get all bookings and categorize them
    all_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    upcoming_bookings = all_bookings.filter(
        is_cancelled=False,
        showtime__date__gte=current_date
    )

    past_bookings = all_bookings.filter(
        is_cancelled=False,
        showtime__date__lt=current_date
    )

    cancelled_bookings = all_bookings.filter(
        is_cancelled=True
    )

    # Calculate rewards
    profile.calculate_rewards()
    rewards_points = profile.rewards_points

    # Rewards
    rewards = [
        {'id': 1, 'name': 'Free Small Popcorn', 'description': 'Enjoy a free small popcorn on your next visit',
         'points_required': 50},
        {'id': 2, 'name': '10% Off Next Booking', 'description': 'Get 10% discount on your next movie booking',
         'points_required': 100},
        {'id': 3, 'name': '25% Off Next Booking', 'description': 'Get 25% discount on your next movie booking',
         'points_required': 200},
        {'id': 4, 'name': 'VIP Lounge Access', 'description': 'Exclusive access to VIP lounge for one show',
         'points_required': 300}
    ]

    # Get names of claimed rewards
    claimed_rewards = UserReward.objects.filter(
        user=request.user,
        reward_name__in=[r['name'] for r in rewards]
    ).values_list('reward_name', flat=True)

    return render(request, 'booking_system/profile.html', {
        'profile': profile,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'cancelled_bookings': cancelled_bookings,
        'bookings_count': all_bookings.count(),
        'rewards_points': profile.rewards_points,
        'rewards_progress': min(100, (profile.rewards_points % 100)),
        'rewards_needed': max(0, 100 - (profile.rewards_points % 100)),
        'rewards': rewards,
        'claimed_rewards': claimed_rewards,
        'current_date': current_date,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'booking_system/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'booking_system/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_edit_view(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'booking_system/profile_edit.html', {
        'form': form,
        'profile': profile
    })


@login_required
def claim_reward(request, reward_id):
    profile = request.user.userprofile

    sample_rewards = {
        1: {'name': 'Free Small Popcorn', 'points_required': 50},
        2: {'name': '10% Off Next Booking', 'points_required': 100},
        3: {'name': '25% Off Next Booking', 'points_required': 200},
        4: {'name': 'VIP Lounge Access', 'points_required': 300}
    }

    if reward_id not in sample_rewards:
        messages.error(request, 'Invalid reward')
        return redirect('profile')

    reward_data = sample_rewards[reward_id]

    if profile.rewards_points >= reward_data['points_required']:
        # Generate unique code
        while True:
            code = 'CINE-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not UserReward.objects.filter(code=code).exists():
                break

        UserReward.objects.create(
            user=request.user,
            reward_name=reward_data['name'],
            reward_points=reward_data['points_required'],
            code=code
        )
        profile.rewards_points -= reward_data['points_required']
        profile.save()
        messages.success(request, f'Reward claimed! Your code: {code}')
    else:
        messages.error(request, 'Not enough points to claim this reward.')

    return redirect('profile')


@login_required
def check_reward_code(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        try:
            reward = UserReward.objects.get(
                code=code,
                user=request.user,
                is_active=True
            )
            if reward.is_used:
                return JsonResponse({'valid': False, 'message': 'This code has already been used'})
            return JsonResponse({
                'valid': True,
                'reward': reward.reward_name,
                'message': f'Valid code for: {reward.reward_name}'
            })
        except UserReward.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Invalid code'})

    return JsonResponse({'valid': False, 'message': 'Invalid request'})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.is_cancelled:
        messages.error(request, "This booking is already cancelled")
        return redirect('profile')

    if booking.showtime.date < timezone.now().date():
        messages.error(request, "Cannot cancel past bookings")
        return redirect('profile')

    # Mark seats as available by deleting BookedSeat records
    booked_seats = booking.bookedseat_set.all()
    for booked_seat in booked_seats:
        # Optional: Mark seat as available if you're using is_booked flag
        booked_seat.seat.is_booked = False
        booked_seat.seat.save()

    # Delete the booked seat records
    booked_seats.delete()

    # Deduct rewards points if this was a confirmed booking
    profile = request.user.userprofile
    if not booking.is_cancelled:  # Only deduct if wasn't already cancelled
        profile.rewards_points = max(0, profile.rewards_points - 10)
        profile.save()

    # Mark booking as cancelled
    booking.is_cancelled = True
    booking.cancelled_at = timezone.now()
    booking.save()

    messages.success(request, "Booking cancelled successfully. 10 reward points deducted.")
    return redirect('profile')