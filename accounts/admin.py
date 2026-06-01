from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('display_name', 'email', 'phone', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('display_name', 'email', 'phone')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('display_name', 'phone', 'national_id_number', 'fayda_fin')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'display_name', 'phone', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)