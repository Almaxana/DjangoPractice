from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

from .views import TimeSheetEntryView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('timesheet-entry/', TimeSheetEntryView.as_view(), name='timesheet_add'),  # POST
    path('timesheet-entry/<int:entry_id>/', TimeSheetEntryView.as_view(), name='timesheet_modify'),  # PUT, DELETE

    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout-page/', views.logout_page_view, name='logout_page'),
    path('logout/', auth_views.LogoutView.as_view(next_page='register'), name='logout_action'),
]