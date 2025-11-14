import logging
from functools import wraps

from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from django.contrib.auth import authenticate
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser, User
from django.http import JsonResponse

from config.settings.base import CLERK_AUTHORIZED_PARTIES, CLERK_SECRET_KEY

logger = logging.getLogger(__name__)


class JwtAuthBackend(BaseBackend):
    def authenticate(self, request, **_kwargs):
        try:
            state = authenticate_request(
                request,
                AuthenticateRequestOptions(
                    secret_key=CLERK_SECRET_KEY,
                    authorized_parties=CLERK_AUTHORIZED_PARTIES,
                ),
            )

            if not state.is_signed_in:
                request.error_message = getattr(state, "message", "Not signed in")
                logger.warning(
                    "JWT auth: Clerk rejected token: %s", request.error_message
                )
                return None

            request.auth_payload = state.payload

            django_user = AnonymousUser()
            django_user.username = state.payload.get("sub") or "clerk_user"
            return django_user

        except Exception:
            request.error_message = "Unable to authenticate user"
            logger.exception("JWT auth: exception during authentication")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Exception:
            return None


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = authenticate(request)  # triggers JwtAuthBackend.authenticate
        if not user:
            error = getattr(request, "error_message", "User not authenticated")
            return JsonResponse({"detail": error}, status=401)
        request.user = user

        # Extract user_id and is_admin from auth_payload (set by JwtAuthBackend)
        auth_payload = getattr(request, "auth_payload", {})
        request.user_id = auth_payload.get("sub") or auth_payload.get("id")
        request.is_admin = auth_payload.get("role") == "admin"

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def optional_jwt(view_func):
    """
    Optional JWT authentication decorator.
    If a token is provided and valid, populates request.auth_payload, request.user_id, and request.is_admin.
    If no token or invalid token, continues without error (for public endpoints).
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            state = authenticate_request(
                request,
                AuthenticateRequestOptions(
                    secret_key=CLERK_SECRET_KEY,
                    authorized_parties=CLERK_AUTHORIZED_PARTIES,
                ),
            )

            if state.is_signed_in:
                request.auth_payload = state.payload
                # Extract user_id (tries 'sub' first, falls back to 'id')
                request.user_id = state.payload.get("sub") or state.payload.get("id")
                # Check if user is admin
                request.is_admin = state.payload.get("role") == "admin"
                django_user = AnonymousUser()
                django_user.username = request.user_id or "clerk_user"
                request.user = django_user
            else:
                # No token or invalid token - that's fine, just continue
                request.auth_payload = {}
                request.user_id = None
                request.is_admin = False
                request.user = AnonymousUser()
        except Exception:
            # Any error during auth - that's fine, just continue
            request.auth_payload = {}
            request.user_id = None
            request.is_admin = False
            request.user = AnonymousUser()

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request, "is_admin", False):
            return JsonResponse({"message": "Admin only"}, status=403)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
