"""szyyw-auth — trust the identity headers the szyyw.xyz Caddy gate injects.

The gate (Caddy forward_auth -> portal /api/auth/verify) only lets a request
through when the portal session is valid and the user may open this site; it
then adds X-User / X-Role / X-Portal-Sub. Those headers are trustworthy ONLY
because the app container is reachable solely via Caddy (no published ports).

Enable with SZYYW_SSO=1. When unset, every helper returns None / refuses, so
local development keeps the app's own login.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import quote

__version__ = "0.1.0"

HEADER_USER = "X-User"
HEADER_ROLE = "X-Role"
HEADER_SUB = "X-Portal-Sub"
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

    Returns None when the user header is absent, i.e. the request did not come
    through the gate. Callers must treat that as unauthenticated.
    """
    user = (get(HEADER_USER) or "").strip()
    if not user:
        return None
    role = (get(HEADER_ROLE) or "user").strip().lower()
    if role not in ROLES:
        role = "user"
    sub = (get(HEADER_SUB) or user).strip()
    return Identity(user=user, role=role, sub=sub)


def login_url(portal: str, return_to: str) -> str:
    """Where to send an unauthenticated browser: portal login that returns to `return_to`."""
    return f"{portal.rstrip('/')}/login?rd={quote(return_to, safe='')}"
