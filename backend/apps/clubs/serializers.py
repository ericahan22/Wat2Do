from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Clubs


class ClubSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for user club submissions"""
    
    class Meta:
        model = Clubs
        fields = [
            'club_name', 'categories', 'club_page', 'ig', 'discord', 'club_type'
        ]
    
    def validate_club_name(self, value):
        """Ensure club name is not empty and unique"""
        if not value.strip():
            raise serializers.ValidationError("Club name cannot be empty")
        
        # Check if club already exists (excluding pending submissions)
        if Clubs.objects.filter(club_name__iexact=value.strip(), status__in=['scraped', 'approved']).exists():
            raise serializers.ValidationError("A club with this name already exists")
        
        return value.strip()
    
    def validate_categories(self, value):
        """Ensure categories is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Categories cannot be empty")
        return value.strip()


class ClubSubmissionResponseSerializer(serializers.ModelSerializer):
    """Serializer for club submission responses"""
    
    class Meta:
        model = Clubs
        fields = [
            'id', 'club_name', 'categories', 'club_page', 'ig', 'discord',
            'club_type', 'status', 'submitted_at', 'rejection_reason'
        ]


class ClubModerationSerializer(serializers.ModelSerializer):
    """Serializer for admin club moderation"""
    
    class Meta:
        model = Clubs
        fields = ['status', 'rejection_reason']
    
    def validate_status(self, value):
        """Ensure status is valid for moderation"""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be 'approved' or 'rejected'")
        return value
    
    def validate(self, data):
        """Ensure rejection_reason is provided when rejecting"""
        if data.get('status') == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting a club")
        return data
