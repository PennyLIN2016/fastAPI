# require_https.py: It enforces HTTPS in production (or whenever you want) by issuing a 307 redirect to the HTTPS URL when a non-HTTPS request is received. It also respects X-Forwarded-Proto for deployments behind proxies.
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, ASGIInstance, Receive, Scope, Send
import typing
import os

class RequireHTTPSMiddleware:
    """
    FastAPI/ASGI middleware to redirect HTTP requests to HTTPS.

    Behavior:
    - If running in development (DEBUG != True), it will enforce HTTPS
      by redirecting to https:// URL.
    - If behind a proxy (e.g., behind nginx or a load balancer),
      it will honor X-Forwarded-Proto to determine the original scheme.
    - Uses a 307 redirect to preserve the HTTP method for non-GET requests.
    """

    def __init__(self, app: ASGIApp, debug: bool = False):
        self.app = app
        # If you have an environment flag, prefer that; fallback to param
        self.debug = debug or (os.getenv("DEBUG", "false").lower() == "true")

    def _get_scheme(self, scope: Scope) -> str:
        # Respect X-Forwarded-Proto if present
        headers = dict((k.lower(), v) for k, v in scope.get("headers", []))
        proto = headers.get(b"x-forwarded-proto", b"").decode("utf-8")
        if proto:
            return proto

        # Fallback to the request scheme
        return scope.get("scheme", "http")

    def __call__(self, scope: Scope, receive: Receive, send: Send) -> typing.Awaitable:
        async def send_redirect():
            # Build a redirect URL to https
            scheme = self._get_scheme(scope)
            if scheme == "https":
                # Already https; continue normally
                await self.app(scope, receive, send)
                return

            # Build host and path
            headers = dict((k.lower(), v) for k, v in scope.get("headers", []))
            host = headers.get(b"host", b"").decode("utf-8")
            path = scope.get("path", b"").decode("utf-8")
            query = scope.get("query_string", b"").decode("utf-8")
            full_path = path + (f"?{query}" if query else "")

            https_url = f"https://{host}{full_path}"

            # Issue a 307 redirect
            await send(
                {
                    "type": "http.response.start",
                    "status": 307,
                    "headers": [(b"location", https_url.encode("utf-8"))],
                }
            )
            await send({"type": "http.response.body", "body": b"", "more_body": False})

        # If not HTTP, or already HTTPS, or in debug/development, pass through
        if scope["type"] == "http":
            scheme = self._get_scheme(scope)
            if self.debug or scheme != "https":
                await send_redirect()
                return

        await self.app(scope, receive, send)
