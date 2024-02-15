from django.shortcuts import render

from .models import UserProfile

def profile_card_view(request):
    # Fetch profile data from the database
    profile = UserProfile.objects.first()  # Assuming you want to display the first profile
    # Pass profile data to the template context
    context = {
        'profile': profile
    }
    # Render the template with profile data
    return render(request, 'profiles/profile_card.html', context)