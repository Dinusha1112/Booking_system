from django.shortcuts import render

def home(request):
    return render(request, 'booking_system/home.html')
