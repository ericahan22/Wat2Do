from functools import wraps
import logging

from clerk_backend_api import authenticate_request, AuthenticateRequestOptions
from django.contrib.auth import authenticate
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import JsonResponse

from config.settings.base import CLERK_SECRET_KEY, CLERK_AUTHORIZED_PARTIES
import httpx

logger = logging.getLogger(__name__)


class JwtAuthBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        if 'Authorization' not in request.headers:
            logger.warning("JWT auth: Missing Authorization header on %s %s", request.method, request.path)
            return None

        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header.startswith('Bearer '):
                logger.warning("JWT auth: Authorization header not Bearer on %s %s", request.method, request.path)
                return None

            logger.debug(
                "JWT auth: attempting Clerk auth (aud=%s) on %s %s",
                CLERK_AUTHORIZED_PARTIES,
                request.method,
                request.path,
            )
            request_state = authenticate_request(
                request,
                AuthenticateRequestOptions(
                    secret_key=CLERK_SECRET_KEY,
                    authorized_parties=CLERK_AUTHORIZED_PARTIES,
                ),
            )
            if not request_state.is_signed_in:
                request.error_message = request_state.message
                logger.warning("JWT auth: Clerk rejected token: %s", request_state.message)
                return None
            # Ideally at this point user object must be fetched from DB and returned, but we will just return a dummy
            # user object
            user = User(username=request_state.payload.get("sub", "unknown"), password="None")
            # Attach payload for downstream usage if needed
            try:
                request.auth_payload = request_state.payload
            except Exception:
                pass
            return user

        except Exception as e:
            request.error_message = "Unable to authenticate user"
            logger.exception("JWT auth: exception during authentication")
            return None

    def get_user(self, user_id):
        return User(username=user_id, password="None")


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = authenticate(request)
        if not user:
            error = getattr(request, 'error_message', 'User not authenticated')
            return JsonResponse({'detail': error}, status=401)
        request.user = user
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def is_admin(request) -> bool:
    """Return True if Clerk public metadata contains role == 'admin'."""
    try:
        payload = getattr(request, "auth_payload", {}) or {}
        public_meta = payload.get("public_metadata") or payload.get("publicMetadata") or {}
        if not public_meta:
            user_id = payload.get("sub") or payload.get("id")
            if user_id and CLERK_SECRET_KEY:
                try:
                    with httpx.Client(timeout=5.0) as client:
                        resp = client.get(
                            f"https://api.clerk.com/v1/users/{user_id}",
                            headers={
                                "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                                "Content-Type": "application/json",
                            },
                        )
                        if resp.status_code == 200:
                            data = resp.json() or {}
                            public_meta = data.get("public_metadata") or {}
                            try:
                                request.clerk_user = data
                            except Exception:
                                pass
                except Exception:
                    public_meta = {}
        return public_meta.get("role") == "admin"
    except Exception:
        return False


def admin_required(view_func):
    @wraps(view_func)
    @jwt_required
    def _wrapped_view(request, *args, **kwargs):
        if not is_admin(request):
            return JsonResponse({'detail': 'Admin only'}, status=403)
        return view_func(request, *args, **kwargs)

    return _wrapped_view