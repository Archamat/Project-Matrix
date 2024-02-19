from django.shortcuts import render,redirect
from .forms import InputForm
from .models import UserProfile
from .forms import ProjectFilterForm

def profile_card_view(request):
    # Fetch all profiles from the database
    form = ProjectFilterForm(request.GET)
    profiles = UserProfile.objects.all()
    # Pass profiles data to the template context
    if form.is_valid() and form.cleaned_data['category']:
        profiles = profiles.filter(category=form.cleaned_data['category'])
    context = {
        'profiles': profiles,
        'form': form,
    }
    # Render the template with profiles data
    return render(request, 'profiles/profile_card.html', context)



 
# Create your views here.
def home_view(request):
    if request.method == 'POST':
        form = InputForm(request.POST)

        if form.is_valid():
            Name = form.cleaned_data['Name']
            Age = form.cleaned_data['Age']
            Job = form.cleaned_data['Job']
            Category = form.cleaned_data['Category']
            UserProfile.objects.create(name=Name, age=Age, job=Job,category=Category)
            
    else:
        form = InputForm()

    return render(request, 'profiles/create_profile.html', {'form': form})





