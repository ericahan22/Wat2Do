from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Events


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'date', 'start_time', 'location', 'club_handle', 
        'status_badge', 'submitted_by', 'submitted_at', 'email_verified_status'
    ]
    list_filter = [
        'status', 'club_type', 'date', 'submitted_at', 'submitted_by'
    ]
    search_fields = ['name', 'club_handle', 'location', 'description', 'submitted_by__username', 'submitted_by__email']
    readonly_fields = ['added_at', 'submitted_at', 'reviewed_at', 'embedding']
    actions = ['approve_events', 'reject_events']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'date', 'start_time', 'end_time', 'location', 'description')
        }),
        ('Club Information', {
            'fields': ('club_handle', 'club_type', 'url')
        }),
        ('Event Options', {
            'fields': ('price', 'food', 'registration', 'image_url')
        }),
        ('Submission Information', {
            'fields': ('status', 'submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('added_at', 'embedding', 'reactions', 'notes'),
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

    def approve_events(self, request, queryset):
        """Bulk approve events"""
        updated = queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} events were successfully approved.')
    approve_events.short_description = "Approve selected events"

    def reject_events(self, request, queryset):
        """Bulk reject events"""
        updated = queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} events were successfully rejected.')
    reject_events.short_description = "Reject selected events"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submitted_by', 'reviewed_by')
