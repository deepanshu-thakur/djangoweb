from django.contrib import admin
from django.urls import path, reverse_lazy
from website import views
from . import views
app_name='website'

urlpatterns = [
    path('',views.index,name='home'), 
    path('about',views.about,name='about'), 
    path('services',views.services,name='services'),
    path('contact',views.contact,name='contact'),
    #============================================
]