from django.contrib import admin

from .models import Worker, Project, TimeSheetItem

admin.site.register(Worker)
admin.site.register(Project)
admin.site.register(TimeSheetItem)
