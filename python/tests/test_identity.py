import pytest

from szyyw_auth import identity_from_headers, is_anonymous

FULL = {"X-User": "alice", "X-Role": "admin", "X-Portal-Sub": "u1"}
ANON = {"X-Portal-Anon": "1"}


def getter(h):
    low = {k.lower(): v for k, v in h.items()}
    return lambda n: low.get(n.lower())


@pytest.fixture(autouse=True)
def sso(monkeypatch):
    monkeypatch.setenv("SZYYW_SSO", "1")


def test_full_headers():
    i = identity_from_headers(getter(FULL))
    assert (i.user, i.role, i.sub, i.is_admin) == ("alice", "admin", "u1", True)


def test_role_defaults_to_user():
    assert identity_from_headers(getter({"X-User": "a", "X-Portal-Sub": "s"})).role == "user"


def test_user_without_sub_is_none():
    assert identity_from_headers(getter({"X-User": "alice"})) is None
    assert identity_from_headers(getter({"X-User": "alice", "X-Portal-Sub": " "})) is None


def test_anon():
    g = getter(ANON)
    assert identity_from_headers(g) is None
    assert is_anonymous(g) is True
    assert is_anonymous(getter({"X-Portal-Anon": "0"})) is False
    assert is_anonymous(getter({})) is False


def test_anon_plus_identity_identity_wins():
    g = getter({**FULL, **ANON})
    assert identity_from_headers(g).user == "alice"
    assert is_anonymous(g) is False


def test_flask_adapter():
    flask = pytest.importorskip("flask")
    from szyyw_auth.flask import (current_identity, is_anonymous as anon,
                                  optional_identity, require_identity)

    app = flask.Flask(__name__)

    @app.get("/req")
    @require_identity()
    def r():
        return "ok"

    @app.get("/opt")
    @optional_identity
    def o():
        i = flask.g.identity
        return {"user": i.user if i else None, "anon": anon()}

    c = app.test_client()
    assert c.get("/req", headers=ANON).status_code == 401
    assert c.get("/req").status_code == 401
    assert c.get("/req", headers=FULL).status_code == 200
    assert c.get("/opt", headers=ANON).get_json() == {"user": None, "anon": True}
    assert c.get("/opt", headers=FULL).get_json() == {"user": "alice", "anon": False}


def test_starlette_adapter():
    pytest.importorskip("starlette")
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.testclient import TestClient

    from szyyw_auth.starlette import (is_anonymous as anon, optional_identity,
                                      require_admin, require_identity)

    async def req(request):
        return JSONResponse({"user": require_identity(request).user})

    async def adm(request):
        return JSONResponse({"user": require_admin(request).user})

    async def opt(request):
        i = optional_identity(request)
        return JSONResponse({"user": i.user if i else None, "anon": anon(request)})

    from starlette.exceptions import HTTPException  # noqa: F401
    app = Starlette(routes=[Route("/req", req), Route("/adm", adm), Route("/opt", opt)])
    c = TestClient(app)
    assert c.get("/req", headers=ANON).status_code == 401
    assert c.get("/req", headers=FULL).status_code == 200
    assert c.get("/adm", headers={**FULL, "X-Role": "user"}).status_code == 403
    assert c.get("/opt", headers=ANON).json() == {"user": None, "anon": True}
    assert c.get("/opt", headers=FULL).json() == {"user": "alice", "anon": False}
