from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Worker


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        help_text='',
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
        widget=forms.TextInput(attrs={'autocapitalize': 'none'})
    )

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + ('position',)
