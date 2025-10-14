from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Clubs


@admin.register(Clubs)
class ClubsAdmin(admin.ModelAdmin):
    list_display = [
        'club_name', 'club_type', 'status_badge', 'submitted_by', 
        'submitted_at', 'email_verified_status'
    ]
    list_filter = [
        'status', 'club_type', 'submitted_at', 'submitted_by'
    ]
    search_fields = ['club_name', 'categories', 'submitted_by__username', 'submitted_by__email']
    readonly_fields = ['submitted_at', 'reviewed_at']
    actions = ['approve_clubs', 'reject_clubs']
    
    fieldsets = (
        ('Club Details', {
            'fields': ('club_name', 'categories', 'club_type')
        }),
        ('Contact Information', {
            'fields': ('club_page', 'ig', 'discord')
        }),
        ('Submission Information', {
            'fields': ('status', 'submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'approved': 'green',
            'pending': 'orange', 
            'rejected': 'red',
            'scraped': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'

    def email_verified_status(self, obj):
        """Show if submitter's email is verified"""
        if obj.submitted_by and hasattr(obj.submitted_by, 'profile'):
            if obj.submitted_by.profile.email_verified:
                return format_html('<span style="color: green;">✓ Verified</span>')
            else:
                return format_html('<span style="color: red;">✗ Unverified</span>')
        return '-'
    email_verified_status.short_description = 'Email Status'

    def approve_clubs(self, request, queryset):
        """Bulk approve clubs"""
        updated = queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} clubs were successfully approved.')
    approve_clubs.short_description = "Approve selected clubs"

    def reject_clubs(self, request, queryset):
        """Bulk reject clubs"""
        updated = queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} clubs were successfully rejected.')
    reject_clubs.short_description = "Reject selected clubs"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submitted_by', 'reviewed_by')
