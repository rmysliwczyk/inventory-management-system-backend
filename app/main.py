import os
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import text

from .dependencies import IntegrityErrorHandler, get_session
from .initialize_database import initialize_database
from .routes.asset_types import router as asset_types_router
from .routes.assets import router as assets_router
from .routes.auth import router as auth_router
from .routes.users import router as users_router

load_dotenv()

DATABASE_SYSTEM = os.environ.get("DATABASE_SYSTEM")


@asynccontextmanager
async def mylifespan(app: FastAPI):
    # Sets up the database and creates tables and initial account if needed.
    initialize_database()
    yield


app = FastAPI(lifespan=mylifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


@app.get("/status/")
def check_api_status() -> str:
    return "API is reachable."


app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(users_router)
app.include_router(asset_types_router)

app.add_exception_handler(IntegrityError, IntegrityErrorHandler)
