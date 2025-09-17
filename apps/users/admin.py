from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with additional fields.
    """
    list_display = ('email', 'username', 'first_name', 'last_name',
                    'is_active', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_verified', 'is_staff',
                   'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number',
         'date_of_birth', 'profile_picture', 'bio', 'location', 'website')}),
        ('Permissions', {'fields': ('is_active', 'is_verified',
         'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin.
    """
    list_display = ('user', 'location', 'birth_date', 'phone_number', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('user__email', 'user__first_name',
                     'user__last_name', 'location', 'phone_number')
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Information', {'fields': ('avatar', 'bio',
         'location', 'birth_date', 'phone_number', 'website')}),
        ('Social Links', {'fields': ('social_links',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
