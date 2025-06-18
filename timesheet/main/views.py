import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TimeSheetItem, Project, Worker
from .forms import CustomUserCreationForm
from .serializers import TimeSheetItemSerializer


@login_required
def home(request):
    requested_employee_id_filter = request.GET.get('employee')
    filter_start_date = request.GET.get('start_date')
    filter_end_date = request.GET.get('end_date')

    timesheet_query = TimeSheetItem.objects.select_related('worker', 'project')

    effective_employee_id_for_template = None

    if request.user.is_staff:
        if requested_employee_id_filter:
            timesheet_query = timesheet_query.filter(worker_id=requested_employee_id_filter)
            effective_employee_id_for_template = requested_employee_id_filter
    else:
        timesheet_query = timesheet_query.filter(worker=request.user)
        effective_employee_id_for_template = str(request.user.id)

    if filter_start_date:
        timesheet_query = timesheet_query.filter(date__gte=filter_start_date)
    if filter_end_date:
        timesheet_query = timesheet_query.filter(date__lte=filter_end_date)

    timesheet = timesheet_query.order_by('-date')
    projects = Project.objects.all()
    employees = Worker.objects.all()

    current_filters = {
        'employee': effective_employee_id_for_template,
        'start_date': filter_start_date,
        'end_date': filter_end_date,
    }

    return render(request, 'main/home.html', {
        'timeSheet': timesheet,
        'projects': projects,
        'employees': employees,
        'current_filters': current_filters,
        'current_user': request.user,
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('home')
            except Exception as e:
                print(f"Ошибка при регистрации: {e}")
                messages.error(request, 'Произошла ошибка при регистрации. Попробуйте еще раз.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})


class TimeSheetEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entry_id=None):
        if entry_id is not None:
            return Response({'success': False, 'error': 'POST с ID не поддерживается'}, status=405)

        serializer = TimeSheetItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    def put(self, request, entry_id=None):
        if entry_id is None:
            return Response({'success': False, 'error': 'PUT требует ID записи'}, status=400)

        entry = get_object_or_404(TimeSheetItem, id=entry_id)
        if entry.worker != request.user and not request.user.is_staff:
            return Response({'success': False, 'error': 'Нет прав на редактирование.'}, status=403)

        serializer = TimeSheetItemSerializer(entry, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Запись обновлена.',
                'entry': serializer.data
            })
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    def delete(self, request, entry_id=None):
        print(f"DELETE request received for entry_id={entry_id} by user={request.user}")

        if entry_id is None:
            return Response({'success': False, 'error': 'DELETE требует ID записи'}, status=400)

        entry = get_object_or_404(TimeSheetItem, id=entry_id)
        if entry.worker != request.user and not request.user.is_staff:
            return Response({'success': False, 'error': 'Нет прав на удаление.'}, status=403)

        entry.delete()
        return Response({'success': True, 'message': 'Запись удалена.'})


@login_required
def logout_page_view(request):
    return render(request, 'main/logout_page.html')
