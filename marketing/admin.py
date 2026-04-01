from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Marketing', {'fields': ('role', 'phone_number', 'mfa_secret', 'is_mfa_enabled')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Marketing', {'fields': ('role', 'phone_number', 'email')}),
    )

admin.site.register(User, CustomUserAdmin)