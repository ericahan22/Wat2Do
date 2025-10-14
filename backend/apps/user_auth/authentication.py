"""
Custom authentication classes for Django REST Framework.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class CookieTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class that authenticates users via auth_token cookie.
    """
    
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if authentication should
        succeed, otherwise `None`.
        """
        auth_token = request.COOKIES.get('auth_token')
        
        if not auth_token:
            return None
            
        try:
            token = Token.objects.get(key=auth_token)
            return (token.user, token)
        except Token.DoesNotExist:
            return None
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Cookie'
