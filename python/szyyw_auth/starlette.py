"""Starlette / FastAPI adapter.

    from szyyw_auth.starlette import require_identity, require_admin
    @app.get("/x")
    def x(ident: Identity = Depends(require_identity)): ...
"""
from __future__ import annotations

from typing import Optional

from starlette.exceptions import HTTPException
from starlette.requests import Request

from . import Identity, identity_from_headers, sso_enabled

_MISSING = object()


def current_identity(request: Request) -> Optional[Identity]:
    """Identity for this request, or None (SSO off, or the request bypassed the gate)."""
    if not sso_enabled():
        return None
    cached = request.scope.get("szyyw_identity", _MISSING)
    if cached is _MISSING:
        cached = identity_from_headers(request.headers.get)
        request.scope["szyyw_identity"] = cached
    return cached


def require_identity(request: Request) -> Identity:
    ident = current_identity(request)
    if ident is None:
        raise HTTPException(401, "unauthorized")
    return ident


def require_admin(request: Request) -> Identity:
    ident = require_identity(request)
    if not ident.is_admin:
        raise HTTPException(403, "forbidden")
    return ident
