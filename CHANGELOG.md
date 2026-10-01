# Changelog

## v0.2.0 — 2026-10-02

- **行为变更（修复）**：只有 `X-User`、没有 `X-Portal-Sub` 的请求现在视为**未认证**（`identity_from_headers` / `identityFromHeaders` 返回 `None`/`null`）。v0.1.0 会静默用 `X-User` 填 `sub`。身份需要 `X-User` 与 `X-Portal-Sub` 都非空；`X-Role` 缺省仍为 `user`。门卫（portal verify）一直同时发这两个头，正常流量不受影响；直接构造头的测试/脚本需补上 `X-Portal-Sub`。
- 新增匿名身份：门卫对允许匿名的站点的匿名访客注入 `X-Portal-Anon: 1`（与身份头二选一）。`is_anonymous` / `isAnonymousFromHeaders`；适配层 `szyyw_auth.flask.is_anonymous()`、`szyyw_auth.starlette.is_anonymous(request)`、express `isAnonymous(req)`、next `isAnonymousFromRequestHeaders(headers)`。匿名时 `current_identity` / `identity` 返回 `None`/`null`；两类头同时出现时身份优先。
- 新增 `optional_identity`（Flask 装饰器，设置 `g.identity`；Starlette 依赖）、`optionalIdentity()`（Express 中间件，设置 `req.identity`）、`optionalIdentity(headers)`（Next，同 `identityFromRequestHeaders`）：不拒绝，匿名/未登录得到 `None`/`null`。
- `require_identity` / `requireIdentity` / `require_admin` 不变：匿名与「无身份」同样 401（API）。
- `HEADERS` 增加 `anon`；Python 增加 `HEADER_ANON`。身份对象形状不变：`{user, role, sub}`（JS 另有派生的 `isAdmin`，Python 为 `is_admin` 属性）。
- 增加测试：`python/tests`（pytest）、`test/`（`npm test`）。

## v0.1.0 — 2026-10-01

- 首发。`identity_from_headers` / `identityFromHeaders`、`sso_enabled` / `ssoEnabled`、`login_url` / `loginUrl`。
- Python 适配：`szyyw_auth.flask`（`current_identity`、`require_identity`）、`szyyw_auth.starlette`（`current_identity`、`require_identity`、`require_admin`）。
- JS 适配：`@szyyw/auth/express`（`identity`、`requireIdentity`）、`@szyyw/auth/next`（`identityFromRequestHeaders`）。
