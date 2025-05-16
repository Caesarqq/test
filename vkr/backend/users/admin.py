from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Charity, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_active', 'is_email_verified')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Roles'), {'fields': ('role', 'is_email_verified')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Charity)
admin.site.register(Notification)
