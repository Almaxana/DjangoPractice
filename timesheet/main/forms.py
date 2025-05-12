# <your_app_name>/forms.py (Пример формы регистрации)
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Worker # Используем нашу модель

class CustomUserCreationForm(UserCreationForm):
    position = forms.CharField(max_length=100, label="Должность", required=False) # Добавляем поле

    class Meta(UserCreationForm.Meta):
        model = Worker # Указываем нашу модель
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'position',) # Добавляем поля в форму

