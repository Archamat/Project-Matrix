# In profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_card_view, name='project_card'),
    path('create', views.home_view, name='project_create'),
]
