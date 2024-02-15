# In profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_card_view, name='profile_card'),
]
