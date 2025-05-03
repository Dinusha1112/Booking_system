from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    profile.calculate_rewards()

    # Sample rewards
    rewards = [
        {'id': 1, 'name': 'Free Small Popcorn', 'description': 'Enjoy a free small popcorn on your next visit', 'points_required': 50},
        {'id': 2, 'name': '10% Off Next Booking', 'description': 'Get 10% discount on your next movie booking', 'points_required': 100},
        {'id': 3, 'name': 'Free Movie Ticket', 'description': 'Redeem for one free standard movie ticket', 'points_required': 200},
        {'id': 4, 'name': 'VIP Lounge Access', 'description': 'Exclusive access to VIP lounge for one show', 'points_required': 300}
    ]

    # Get names of claimed rewards
    claimed_rewards = UserReward.objects.filter(
        user=request.user,
        reward_name__in=[r['name'] for r in rewards]
    ).values_list('reward_name', flat=True)

    return render(request, 'booking_system/profile.html', {
        'profile': profile,
        'bookings': bookings,
        'bookings_count': bookings.count(),
        'rewards_points': profile.rewards_points,
        'rewards_progress': min(100, (profile.rewards_points % 100)),
        'rewards_needed': max(0, 100 - (profile.rewards_points % 100)),
        'rewards': rewards,
        'claimed_rewards': claimed_rewards
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
        3: {'name': 'Free Movie Ticket', 'points_required': 200},
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