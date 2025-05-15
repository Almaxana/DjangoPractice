from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('add-entry/', views.add_timesheet_entry, name='add_timesheet_entry'),
    path('delete-entry/<int:entry_id>/', views.delete_timesheet_entry, name='delete_timesheet_entry'),
    path('update-entry/<int:entry_id>/', views.update_timesheet_entry, name='update_timesheet_entry'),
]
