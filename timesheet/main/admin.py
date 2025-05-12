from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker, Project, TimeSheetItem


class CustomUserAdmin(UserAdmin):
    UserAdmin.fieldsets[1][1]['fields'] = ('position',)
    UserAdmin.add_fieldsets += (
        (None, {'fields': ('position',)}),
    )
    list_display = ('username', 'is_staff', 'position')


admin.site.register(Worker, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(TimeSheetItem)
