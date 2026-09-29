
import os
import re
import jwt

from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ldap3 import Server, Connection, ALL

app = FastAPI(
    title="LDAP Authentication API",
    description="LDAP authentication with JWT",
    version="2.0.0",
)

LDAP_HOST = os.getenv("LDAP_HOST", "openldap")
LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "dc=example,dc=com")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest):
    # Evita caracteres inesperados en el identificador LDAP.
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", request.username):
        raise HTTPException(
            status_code=400,
            detail="Invalid username format",
        )

    server = Server(
        LDAP_HOST,
        port=LDAP_PORT,
        get_info=ALL,
    )

    user_dn = (
        f"uid={request.username},"
        f"ou=users,"
        f"{LDAP_BASE_DN}"
    )

    connection = Connection(
        server,
        user=user_dn,
        password=request.password,
        auto_bind=False,
    )

    try:
        if not connection.bind():
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        token = create_access_token(request.username)

        return {
            "authenticated": True,
            "username": request.username,
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": JWT_EXPIRE_MINUTES * 60,
        }

    finally:
        connection.unbind()