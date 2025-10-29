from django.http import HttpResponse

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info == '/health':
            return HttpResponse("OK")
        return self.get_response(request)


import os
from typing import Optional

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

try:
    import jwt
    from jwt import PyJWKClient
except Exception:  # pragma: no cover
    jwt = None
    PyJWKClient = None


class ClerkJWKSAuthMiddleware(MiddlewareMixin):
    """
    Minimal Clerk JWT validator using JWKS.
    - Reads Bearer token from Authorization header
    - Fetches signing key from CLERK_JWKS_URL
    - Verifies RS256 signature and issuer (CLERK_ISSUER if set)
    - On success attaches decoded claims to request.clerk_user
    """

    def process_request(self, request: HttpRequest):  # type: ignore[override]
        token = self._extract_bearer_token(request)
        if not token:
            return None

        if jwt is None or PyJWKClient is None:
            # PyJWT is required; silently skip so views can still be accessed if allowed
            return None

        jwks_url = os.getenv("CLERK_JWKS_URL", "https://clerk.wat2do.ca/.well-known/jwks.json")
        issuer = os.getenv("CLERK_ISSUER")

        try:
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            options = {"verify_aud": False}
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=None,
                issuer=issuer if issuer else None,
                options=options,
            )

            # Attach claims for downstream permissions
            setattr(request, "clerk_user", decoded)
        except Exception:
            # Invalid token; do not attach clerk_user. Downstream permissions will deny.
            return None

        return None

    @staticmethod
    def _extract_bearer_token(request: HttpRequest) -> Optional[str]:
        auth_header = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization")
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None