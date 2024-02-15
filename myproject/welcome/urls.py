# In profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page_view, name='welcome_page'),
]
