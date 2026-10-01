"""Flask adapter: `from szyyw_auth.flask import current_identity, require_identity`."""
from __future__ import annotations

from functools import wraps
from typing import Optional

from flask import abort, g, request

from . import Identity, identity_from_headers, is_anonymous as _is_anonymous, sso_enabled


def current_identity() -> Optional[Identity]:
    """Identity for this request, or None (SSO off, or the request bypassed the gate)."""
    if not sso_enabled():
        return None
    if not hasattr(g, "_szyyw_identity"):
        g._szyyw_identity = identity_from_headers(request.headers.get)
    return g._szyyw_identity


def is_anonymous() -> bool:
    """True for an anonymous visitor (X-Portal-Anon: 1, no identity). False when SSO is off."""
    return sso_enabled() and _is_anonymous(request.headers.get)


def optional_identity(fn):
    """Decorator: never rejects. Sets `flask.g.identity` to the Identity or None, then calls fn."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.identity = current_identity()
        return fn(*args, **kwargs)

    return wrapper


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
