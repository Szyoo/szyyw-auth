"""szyyw-auth — trust the identity headers the szyyw.xyz Caddy gate injects.

The gate (Caddy forward_auth -> portal /api/auth/verify) only lets a request
through when the portal session is valid and the user may open this site; it
then adds X-User / X-Role / X-Portal-Sub (or X-Portal-Anon: 1 for an
anonymous visitor on a site that allows anonymous access). Those headers are trustworthy ONLY
because the app container is reachable solely via Caddy (no published ports).

Enable with SZYYW_SSO=1. When unset, every helper returns None / refuses, so
local development keeps the app's own login.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import quote

__version__ = "0.2.0"

HEADER_USER = "X-User"
HEADER_ROLE = "X-Role"
HEADER_SUB = "X-Portal-Sub"
HEADER_ANON = "X-Portal-Anon"
ROLES = ("user", "admin")


def sso_enabled() -> bool:
    return os.environ.get("SZYYW_SSO", "").strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Identity:
    user: str
    role: str
    sub: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def identity_from_headers(get: Callable[[str], Optional[str]]) -> Optional[Identity]:
    """Build an Identity from a header getter (name -> value or None).

    Identity requires BOTH X-User and X-Portal-Sub to be non-empty; otherwise
    returns None and callers must treat the request as unauthenticated (this
    includes anonymous visitors, see is_anonymous). X-Role defaults to "user".
    """
    user = (get(HEADER_USER) or "").strip()
    sub = (get(HEADER_SUB) or "").strip()
    if not user or not sub:
        return None
    role = (get(HEADER_ROLE) or "user").strip().lower()
    if role not in ROLES:
        role = "user"
    return Identity(user=user, role=role, sub=sub)


def is_anonymous(get: Callable[[str], Optional[str]]) -> bool:
    """True for an anonymous visitor on a site that allows anonymous access.

    The gate sends X-Portal-Anon: 1 *instead of* identity headers, never both.
    If both somehow arrive, identity wins and this returns False.
    """
    if identity_from_headers(get) is not None:
        return False
    return (get(HEADER_ANON) or "").strip() == "1"


def login_url(portal: str, return_to: str) -> str:
    """Where to send an unauthenticated browser: portal login that returns to `return_to`."""
    return f"{portal.rstrip('/')}/login?rd={quote(return_to, safe='')}"
