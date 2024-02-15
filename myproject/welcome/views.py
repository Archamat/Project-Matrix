# In welcome/views.py
from django.shortcuts import render

def welcome_page_view(request):
    # Render the welcome page template
    return render(request, 'welcome/welcome.html')
