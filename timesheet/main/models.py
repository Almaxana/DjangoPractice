from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Worker(AbstractUser):
    class PositionChoices(models.TextChoices):
        MANAGER = 'analytic', 'Аналитик'
        DEVELOPER = 'developer', 'Разработчик'
        TESTER = 'tester', 'Тестировщик'

    position = models.CharField(
        "Должность",
        max_length=20,
        choices=PositionChoices.choices,
        default=PositionChoices.DEVELOPER,
    )


    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.username


class Project(models.Model):
    class ProjectStatusChoices(models.TextChoices):
        ACTIVE = 'active', 'активен'
        STOPPED = 'stopped', 'приостановлен'
        CLOSED = 'closed', 'завершен'

    projectStatus = models.CharField(
        "Статус проекта",
        max_length=20,
        choices=ProjectStatusChoices.choices,
        default=ProjectStatusChoices.ACTIVE,
    )
    name = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class TimeSheetItem(models.Model):
    date = models.DateField()
    worker = models.ForeignKey(Worker, on_delete=models.DO_NOTHING, related_name='timesheet_items')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='timesheet_items')
    hours_number = models.PositiveIntegerField()
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Запись о рабочих часах"
        verbose_name_plural = "Записи о рабочих часах"

    def __str__(self):
        return f"{self.date} - {self.worker.username} - {self.project.name} - {self.hours_number}h"
