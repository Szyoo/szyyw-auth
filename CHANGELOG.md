# Changelog

## v0.1.0 — 2026-10-01

- 首发。`identity_from_headers` / `identityFromHeaders`、`sso_enabled` / `ssoEnabled`、`login_url` / `loginUrl`。
- Python 适配：`szyyw_auth.flask`（`current_identity`、`require_identity`）、`szyyw_auth.starlette`（`current_identity`、`require_identity`、`require_admin`）。
- JS 适配：`@szyyw/auth/express`（`identity`、`requireIdentity`）、`@szyyw/auth/next`（`identityFromRequestHeaders`）。
