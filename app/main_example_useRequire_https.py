from fastapi import FastAPI
from .database import Base, engine
from .endpoints import users, items
from .require_https import RequireHTTPSMiddleware

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure REST API")

# Enforce HTTPS (adjust DEBUG as needed)
app.add_middleware(RequireHTTPSMiddleware, debug=False)

# Include routers
app.include_router(users.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/api", tags=["items"])

"""
Notes

If you’re behind a reverse proxy (NGINX, AWS ALB, etc.), ensure they set X-Forwarded-Proto properly.
In production you’ll typically terminate TLS at the proxy and still want the app to see https; this middleware helps ensure clients are redirected to HTTPS when they access HTTP directly.
You can toggle enforcement with an environment variable or by changing the debug parameter.
"""