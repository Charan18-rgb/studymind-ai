from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db, ensure_auth_schema
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
COOKIE_NAME = "studymind_session"


class RegisterBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class LoginBody(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


def _set_session(response: Response, user_id: int) -> None:
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.session_hours)
    token = jwt.encode(
        {"sub": str(user_id), "exp": expires},
        settings.auth_secret,
        algorithm="HS256",
    )
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.session_hours * 3600,
        path="/",
    )


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return "scrypt$16384$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(derived).decode()


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, cost, salt_text, digest_text = encoded.split("$", 3)
        if scheme != "scrypt" or cost != "16384":
            return False
        salt = base64.urlsafe_b64decode(salt_text)
        expected = base64.urlsafe_b64decode(digest_text)
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def user_payload(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/register", status_code=201)
async def register(body: RegisterBody, response: Response, db: AsyncSession = Depends(get_db)):
    await ensure_auth_schema()
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=body.email, name=body.name, password_hash=hash_password(body.password), is_demo=False)
    db.add(user)
    await db.flush()
    _set_session(response, user.id)
    return user_payload(user)


@router.post("/login")
async def login(body: LoginBody, response: Response, db: AsyncSession = Depends(get_db)):
    await ensure_auth_schema()
    user = await db.scalar(select(User).where(User.email == body.email))
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    _set_session(response, user.id)
    return user_payload(user)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax")
    return {"message": "Logged out"}


@router.get("/me")
async def current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user = await resolve_current_user(request, db)
    return user_payload(user)


async def resolve_current_user(request: Request, db: AsyncSession) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Authentication required")
    user = await db.get(User, user_id)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
