from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker, Project, TimeSheetItem


class CustomUserAdmin(UserAdmin):
    UserAdmin.fieldsets[1][1]['fields'] = ('position',)
    UserAdmin.add_fieldsets += (
        (None, {'fields': ('position',)}),
    )
    list_display = ('username', 'is_staff', 'is_active', 'position')

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'projectStatus', 'customer')

    def delete_model(self, request, obj):
        obj.projectStatus = obj.ProjectStatusChoices.CLOSED
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(projectStatus=Project.ProjectStatusChoices.CLOSED)


admin.site.register(Worker, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TimeSheetItem)
