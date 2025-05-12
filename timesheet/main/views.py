from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm
from .models import TimeSheetItem


def home(request):
    timesheet = TimeSheetItem.objects.order_by('-date')
    return render(request, 'main/home.html', {'timeSheet': timesheet})



def register(request):
    if request.method == 'POST':
        # Используем вашу кастомную форму
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Метод save() формы UserCreationForm создаст пользователя
                # и сохранит все поля, указанные в Meta.fields, включая 'position'
                user = form.save()
                login(request, user) # Входим под новым пользователем
                messages.success(request, 'Регистрация прошла успешно!')
                # Замените 'home' на имя URL вашего основного маршрута
                return redirect('home')
            except Exception as e:
                 # Логирование может быть полезным
                 print(f"Ошибка при регистрации: {e}")
                 messages.error(request, 'Произошла ошибка при регистрации. Попробуйте еще раз.')
        else:
             messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else: # GET request
        form = CustomUserCreationForm()

    # Убедитесь, что шаблон 'registration/register.html' существует
    return render(request, 'main/register.html', {'form': form})