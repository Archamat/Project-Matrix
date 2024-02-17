from django.shortcuts import render,redirect
from .forms import InputForm
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



 
# Create your views here.
def home_view(request):
    print("deneme")
    if request.method == 'POST':
        form = InputForm(request.POST)

        if form.is_valid():
            Name = form.cleaned_data['Name']
            Age = form.cleaned_data['Age']
            Job = form.cleaned_data['Job']
            print(f"Name: {Name}, Age: {Age}, Job: {Job}")
            UserProfile.objects.create(name=Name, age=Age, job=Job)
            
    else:
        form = InputForm()

    return render(request, 'profiles/create_profile.html', {'form': form})



