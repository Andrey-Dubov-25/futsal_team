from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'role', 'is_active', 'order')
    list_filter = ('role', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    list_editable = ('is_active', 'order')
    ordering = ('order', 'last_name')
