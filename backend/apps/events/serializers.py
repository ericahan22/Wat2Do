from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Events


class EventSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for user event submissions"""
    
    class Meta:
        model = Events
        fields = [
            'club_handle', 'url', 'name', 'date', 'start_time', 'end_time',
            'location', 'price', 'food', 'registration', 'description',
            'club_type'
        ]
    
    def validate_date(self, value):
        """Ensure event date is in the future"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Event date must be in the future")
        return value
    
    def validate_end_time(self, value):
        """Ensure end time is after start time"""
        start_time = self.initial_data.get('start_time')
        if start_time and value and value <= start_time:
            raise serializers.ValidationError("End time must be after start time")
        return value
    
    def validate_name(self, value):
        """Ensure event name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Event name cannot be empty")
        return value.strip()
    
    def validate_location(self, value):
        """Ensure location is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Location cannot be empty")
        return value.strip()


class EventSubmissionResponseSerializer(serializers.ModelSerializer):
    """Serializer for event submission responses"""
    
    class Meta:
        model = Events
        fields = [
            'id', 'club_handle', 'url', 'name', 'date', 'start_time', 'end_time',
            'location', 'price', 'food', 'registration', 'image_url', 'description',
            'club_type', 'status', 'submitted_at', 'rejection_reason'
        ]


class EventModerationSerializer(serializers.ModelSerializer):
    """Serializer for admin event moderation"""
    
    class Meta:
        model = Events
        fields = ['status', 'rejection_reason']
    
    def validate_status(self, value):
        """Ensure status is valid for moderation"""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be 'approved' or 'rejected'")
        return value
    
    def validate(self, data):
        """Ensure rejection_reason is provided when rejecting"""
        if data.get('status') == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting an event")
        return data
