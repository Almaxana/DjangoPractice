from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('add-entry/', views.add_timesheet_entry, name='add_timesheet_entry'),
]
