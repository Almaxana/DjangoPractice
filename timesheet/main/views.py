from django.shortcuts import render
from .models import TimeSheetItem


def home(request):
    timesheet = TimeSheetItem.objects.order_by('-date')
    return render(request, 'main/home.html', {'timeSheet': timesheet})



