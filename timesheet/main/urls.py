from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('add-entry/', views.add_timesheet_entry, name='add_timesheet_entry'),
    path('delete-entry/<int:entry_id>/', views.delete_timesheet_entry, name='delete_timesheet_entry'),
    path('update-entry/<int:entry_id>/', views.update_timesheet_entry, name='update_timesheet_entry'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout')
]
