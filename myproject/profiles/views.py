from django.shortcuts import render

from .models import UserProfile

def profile_card_view(request):
    # Fetch all profiles from the database
    profiles = UserProfile.objects.all()
    # Pass profiles data to the template context
    context = {
        'profiles': profiles
    }
    # Render the template with profiles data
    return render(request, 'profiles/profile_card.html', context)
