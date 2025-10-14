from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('email_verified', 'verification_token', 'verification_token_created')
    readonly_fields = ('verification_token_created',)


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'email_verified_status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__email_verified')

    def email_verified_status(self, obj):
        """Show if user's email is verified"""
        if hasattr(obj, 'profile'):
            if obj.profile.email_verified:
                return '✓ Verified'
            else:
                return '✗ Unverified'
        return '-'
    email_verified_status.short_description = 'Email Verified'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'verification_token_created', 'created_at')
    list_filter = ('email_verified', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'verification_token_created')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Email Verification', {
            'fields': ('email_verified', 'verification_token', 'verification_token_created')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
