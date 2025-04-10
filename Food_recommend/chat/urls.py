from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.home, name='home'),
    path('room/', views.chat_room, name='chat_room'),
    path('room/assistant/', views.chat_assistant, name='chat_assistant'),
    path('explore/', views.explore, name='explore'),
    path('about/', views.about, name='about'),
    path('nearby-restaurants/', views.nearby_restaurants, name='nearby_restaurants'),
] 