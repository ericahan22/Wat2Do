"""
Simple authentication middleware for Django.
"""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status


class SimpleAuthMiddleware:
    """
    Simple middleware that checks for auth token in cookies and sets request.user
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for auth token in cookies
        auth_token = request.COOKIES.get('auth_token')
        
        if auth_token:
            try:
                token = Token.objects.get(key=auth_token)
                request.user = token.user
                request.auth_token = token
            except Token.DoesNotExist:
                request.user = None
                request.auth_token = None
        else:
            request.user = None
            request.auth_token = None

        response = self.get_response(request)
        return response
