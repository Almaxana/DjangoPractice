# main/views.py
import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt # Лучше не использовать, если CSRF токен настроен

from .forms import CustomUserCreationForm
from .models import TimeSheetItem, Project, Worker  # Добавили Project и Worker


def home(request):
    timesheet_query = TimeSheetItem.objects.select_related('worker', 'project')

    # Получаем значения фильтров из GET-запроса
    filter_employee_id = request.GET.get('employee')
    filter_start_date = request.GET.get('start_date')
    filter_end_date = request.GET.get('end_date')

    # Применяем фильтры, если они есть
    if filter_employee_id:
        timesheet_query = timesheet_query.filter(worker_id=filter_employee_id)
    if filter_start_date:
        timesheet_query = timesheet_query.filter(date__gte=filter_start_date)
    if filter_end_date:
        timesheet_query = timesheet_query.filter(date__lte=filter_end_date)

    timesheet = timesheet_query.order_by('-date')
    projects = Project.objects.all()
    employees = Worker.objects.all()  # Для фильтра сотрудников

    # Передаем значения фильтров обратно в шаблон, чтобы они остались выбранными
    current_filters = {
        'employee': filter_employee_id,
        'start_date': filter_start_date,
        'end_date': filter_end_date,
    }

    return render(request, 'main/home.html', {
        'timeSheet': timesheet,
        'current_user': request.user,
        'projects': projects,  # Передаем проекты
        'employees': employees,  # Передаем сотрудников для фильтра
        'current_filters': current_filters,
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
                print(f"Ошибка при регистрации: {e}")  # Логирование
                messages.error(request, 'Произошла ошибка при регистрации. Попробуйте еще раз.')
        else:
            # Вывод ошибок формы для отладки
            # print(form.errors.as_json())
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})


# @csrf_exempt # Убираем, так как CSRF-токен передается в JS
@login_required
def add_timesheet_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            project_id = data.get('project_id')
            date_val = data.get('date')
            hours_val = data.get('hours_number')  # Убедитесь, что это поле всегда передается
            comment_val = data.get('comment', '')  # Комментарий может быть пустым

            # Валидация на сервере
            if not all([project_id, date_val, hours_val is not None]):  # hours_val может быть 0, но должен быть
                missing = [field for field, val in
                           [('project_id', project_id), ('date', date_val), ('hours_number', hours_val)] if
                           not val and val is not None]
                return JsonResponse({'success': False, 'error': f'Missing required fields: {", ".join(missing)}'},
                                    status=400)

            try:
                # Проверяем, что hours_val можно преобразовать в число
                hours_float = float(hours_val)
                if hours_float < 0:  # Часы не могут быть отрицательными
                    return JsonResponse({'success': False, 'error': 'Hours cannot be negative.'}, status=400)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid hours_number format.'}, status=400)

            try:
                project_instance = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Project not found.'}, status=404)
            except ValueError:  # Если project_id не валидный int/uuid
                return JsonResponse({'success': False, 'error': 'Invalid Project ID format.'}, status=400)

            TimeSheetItem.objects.create(
                date=date_val,
                worker=request.user,
                project=project_instance,  # Используем найденный экземпляр Project
                hours_number=hours_float,  # Используем преобразованное значение
                comment=comment_val
            )
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            print(f"Error in add_timesheet_entry: {type(e).__name__} - {e}")  # Логирование
            return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
