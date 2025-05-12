from django.shortcuts import render

from .models import TimeSheetItem


def main_home(request):
    timeSheet = TimeSheetItem.objects.order_by('-date')
    return render(request, 'main/main_home.html', {'timeSheet': timeSheet})
