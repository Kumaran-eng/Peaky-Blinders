"""Small, server-side password gate for the knowledge-base administration area."""

import secrets

from fastapi import HTTPException, Request, Response, status

from .config import ADMIN_COOKIE_SECURE, ADMIN_PASSWORD

ADMIN_SESSION_COOKIE = "doctrust_admin_session"
_active_sessions: set[str] = set()


def is_admin(request: Request) -> bool:
    """Check whether an HTTP-only session cookie belongs to an active admin session."""
    token = request.cookies.get(ADMIN_SESSION_COOKIE)
    return bool(token and token in _active_sessions)


def require_admin(request: Request) -> None:
    """Protect document management and all admin data from student access."""
    if not is_admin(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin sign-in is required.",
        )


def sign_in(password: str, response: Response) -> None:
    """Verify the configured password and issue an opaque, HTTP-only session cookie."""
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_PASSWORD is not configured on the server.",
        )
    if not secrets.compare_digest(password, ADMIN_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")

    token = secrets.token_urlsafe(32)
    _active_sessions.add(token)
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="strict",
        secure=ADMIN_COOKIE_SECURE,
        max_age=60 * 60 * 8,
        path="/",
    )


def sign_out(request: Request, response: Response) -> None:
    """Invalidate the session server-side and remove the browser cookie."""
    token = request.cookies.get(ADMIN_SESSION_COOKIE)
    if token:
        _active_sessions.discard(token)
    response.delete_cookie(ADMIN_SESSION_COOKIE, path="/")
