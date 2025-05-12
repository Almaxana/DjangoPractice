from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Worker(AbstractUser):
    position = models.CharField("Должность", max_length=100, blank=False, null=False)

    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TimeSheetItem(models.Model):
    date = models.DateField()
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='timesheet_items')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheet_items')
    hours_number = models.PositiveIntegerField()
    comment = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.date} - {self.worker.username} - {self.project.name} - {self.hours_number}h"
