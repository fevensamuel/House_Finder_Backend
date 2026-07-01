from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Hide fields we don't use (first_name, last_name) and show custom ones
    list_display = (
        'id', 'email', 'display_name', 'phone', 'role',
        'is_profile_complete', 'is_active', 'is_staff'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'display_name', 'phone', 'fayda_fin')

    # Fieldsets for the edit form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'display_name', 'phone', 'fayda_fin', 'role', 'avatar'
            )
        }),
        ('Financial & Mobile Wallet', {
            'fields': (
                'cbe_bank_account', 'telebirr_phone', 'cbe_birr_phone'
            )
        }),
        ('ID Documents', {
            'fields': ('id_front', 'id_back')   # ✅ Correct field names
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Pending changes', {
            'fields': ('pending_display_name', 'pending_phone'),
            'classes': ('collapse',)
        }),
        ('FCM Token', {'fields': ('fcm_token',), 'classes': ('collapse',)}),
    )

    # Add form – only essential fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'display_name', 'phone', 'fayda_fin', 'role', 'password1', 'password2'),
        }),
    )

    # Make email required and unique (already enforced by model)
    # Use email as the identifier in admin
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

admin.site.register(User, CustomUserAdmin)