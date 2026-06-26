from fastapi import FastAPI
from .database import Base, engine
from .endpoints import users, items

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure REST API")

# Include routers
app.include_router(users.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/api", tags=["items"])