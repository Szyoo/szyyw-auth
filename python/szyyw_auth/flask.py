"""Flask adapter: `from szyyw_auth.flask import current_identity, require_identity`."""
from __future__ import annotations

from functools import wraps
from typing import Optional

from flask import abort, g, request

from . import Identity, identity_from_headers, sso_enabled


def current_identity() -> Optional[Identity]:
    """Identity for this request, or None (SSO off, or the request bypassed the gate)."""
    if not sso_enabled():
        return None
    if not hasattr(g, "_szyyw_identity"):
        g._szyyw_identity = identity_from_headers(request.headers.get)
    return g._szyyw_identity


def require_identity(role: Optional[str] = None):
    """Decorator: 401 without a gate identity; 403 when role='admin' is required but missing."""

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ident = current_identity()
            if ident is None:
                abort(401)
            if role == "admin" and not ident.is_admin:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return deco
