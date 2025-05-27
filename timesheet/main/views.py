import json

from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import TimeSheetItem, Project, Worker
from .forms import CustomUserCreationForm


@login_required
def home(request):
    requested_employee_id_filter = request.GET.get('employee')
    filter_start_date = request.GET.get('start_date')
    filter_end_date = request.GET.get('end_date')

    timesheet_query = TimeSheetItem.objects.select_related('worker', 'project')

    effective_employee_id_for_template = None

    if request.user.is_superuser:
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


@login_required
def add_timesheet_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            project_id = data.get('project_id')
            date_val = data.get('date')
            hours_val = data.get('hours_number')
            comment_val = data.get('comment', '')

            if not all([project_id, date_val, hours_val is not None]):
                missing = [field for field, val in
                           [('project_id', project_id), ('date', date_val), ('hours_number', hours_val)] if
                           not val and val is not None]
                return JsonResponse({'success': False, 'error': f'Missing required fields: {", ".join(missing)}'},
                                    status=400)

            try:
                hours_float = float(hours_val)
                if hours_float < 0:
                    return JsonResponse({'success': False, 'error': 'Hours cannot be negative.'}, status=400)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid hours_number format.'}, status=400)

            try:
                project_instance = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Project not found.'}, status=404)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid Project ID format.'}, status=400)

            TimeSheetItem.objects.create(
                date=date_val,
                worker=request.user,
                project=project_instance,
                hours_number=hours_float,
                comment=comment_val
            )
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            print(f"Error in add_timesheet_entry: {type(e).__name__} - {e}")
            return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


@login_required
@require_POST
def delete_timesheet_entry(request, entry_id):
    try:
        entry = get_object_or_404(TimeSheetItem, id=entry_id)

        if entry.worker != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'У вас нет прав на удаление этой записи.'}, status=403)

        entry.delete()
        return JsonResponse({'success': True, 'message': 'Запись успешно удалена.'})
    except Exception as e:
        print(f"Ошибка при удалении записи {entry_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def update_timesheet_entry(request, entry_id):
    try:
        entry = get_object_or_404(TimeSheetItem, id=entry_id)

        if entry.worker != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'У вас нет прав на редактирование этой записи.'},
                                status=403)

        data = json.loads(request.body.decode('utf-8'))

        date_str = data.get('date')
        project_id_val = data.get('project_id')
        hours_val = data.get('hours_number')
        comment_val = data.get('comment', entry.comment)

        if not all([date_str, project_id_val, hours_val is not None]):
            missing = [f for f, v in [('date', date_str), ('project_id', project_id_val), ('hours_number', hours_val)]
                       if not v and v is not None]
            return JsonResponse({'success': False, 'error': f'Отсутствуют обязательные поля: {", ".join(missing)}'},
                                status=400)

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат даты. Используйте ГГГГ-ММ-ДД.'},
                                status=400)

        try:
            hours_float = float(hours_val)
            if hours_float < 0:
                return JsonResponse({'success': False, 'error': 'Часы не могут быть отрицательными.'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат количества часов.'}, status=400)

        try:
            project_instance = Project.objects.get(id=project_id_val)
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Проект не найден.'}, status=404)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный ID проекта.'}, status=400)

        entry.date = date_obj
        entry.project = project_instance
        entry.hours_number = hours_float
        entry.comment = comment_val
        entry.save()

        return JsonResponse({
            'success': True,
            'message': 'Запись успешно обновлена.',
            'entry': {
                'id': entry.id,
                'date': entry.date.strftime('%Y-%m-%d'),
                'worker_username': entry.worker.username,
                'project_name': entry.project.name,
                'project_id': entry.project.id,
                'hours_number': entry.hours_number,
                'comment': entry.comment
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный JSON.'}, status=400)
    except Exception as e:
        print(f"Ошибка при обновлении записи {entry_id}: {type(e).__name__} - {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def logout_page_view(request):
    return render(request, 'main/logout_page.html')
