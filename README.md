# szyyw-auth

`*.szyyw.xyz` 各应用的 **SSO 客户端**：读取 Caddy 门卫注入的身份头。Python（Flask / FastAPI / Starlette）和 JS（Express / Next）各一份，无运行时依赖。

## 功能

- 从门卫注入的头构造身份（用户名、本站角色、稳定主体 id）
- 识别允许匿名访问的站点上的匿名访客
- 框架适配：Flask 装饰器、Starlette / FastAPI 依赖、Express 中间件、Next 的 `headers()`
- 生成门户登录地址（登录后跳回）
- `SZYYW_SSO=1` 才启用；未设置时一律返回空 / 拒绝，本地开发继续用应用自己的登录

## 安装

```bash
# Python（Flask / FastAPI / Starlette）
pip install "szyyw-auth @ git+https://github.com/Szyoo/szyyw-auth@v0.2.0#subdirectory=python"
# 可选依赖：szyyw-auth[flask] / szyyw-auth[starlette]

# JS（Express / Next）——用 codeload tarball，node:alpine 里没有 git
npm i "https://codeload.github.com/Szyoo/szyyw-auth/tar.gz/refs/tags/v0.2.0"
```

semver tag 分发，消费方钉精确 tag；变更见 [CHANGELOG.md](CHANGELOG.md)。Python ≥ 3.10。

## 用法

```python
# Flask
from flask import g
from szyyw_auth.flask import current_identity, require_identity, optional_identity, is_anonymous

@app.get("/me")
@require_identity()            # 无身份 401；require_identity("admin") 时非 admin 403
def me():
    ident = current_identity()
    return {"user": ident.user, "role": ident.role}

@app.get("/feed")
@optional_identity             # 不拒绝：g.identity = Identity 或 None
def feed():
    if g.identity is None: ...  # is_anonymous() 区分匿名访客与未经门卫
```

```python
# FastAPI / Starlette
from fastapi import Depends
from szyyw_auth import Identity
from szyyw_auth.starlette import require_identity, require_admin, optional_identity

@app.get("/me")
def me(ident: Identity = Depends(require_identity)): ...      # 401；require_admin 另加 403

@app.get("/feed")
def feed(ident: Identity | None = Depends(optional_identity)): ...   # 不拒绝，匿名 → None
```

```js
// Express
import { requireIdentity, optionalIdentity, isAnonymous } from '@szyyw/auth/express';
app.get('/api/me', requireIdentity(), (req, res) => res.json(req.identity));   // requireIdentity('admin') 时非 admin 403
app.get('/api/feed', optionalIdentity(), (req, res) => res.json({ me: req.identity }));   // 不拒绝，匿名 → null

// Next（route handler / server component）
import { headers } from 'next/headers';
import { identityFromRequestHeaders, isAnonymousFromRequestHeaders } from '@szyyw/auth/next';
const ident = identityFromRequestHeaders(await headers());   // null = 未登录（匿名也是 null）
```

未登录的浏览器导航：`login_url(portal, return_to)` / `loginUrl(portal, returnTo)` 生成 `<portal>/login?rd=<return_to>`。门卫通常已替应用跳转，这个只用于应用自己的回退逻辑。

接入一个应用的典型改动：

1. 用身份头代替自己的 session 查用户；本地用户行按 `sub`（`X-Portal-Sub`）关联，不按用户名。
2. 自己的 `login_required` 换成 `require_identity`；登录页在 `SZYYW_SSO=1` 时 302 到门户。
3. 机器端点（cron、agent、webhook、推送）保持自己的 Bearer token 校验。
4. 保证 `SZYYW_SSO` 未设置时仍能运行。

## 接口说明

### 身份头契约

浏览器 → Caddy `forward_auth` → 门户 `/api/auth/verify`。只有门户会话有效且该用户对本站有权限时请求才会到达应用，并带上：

| 头 | 含义 |
|---|---|
| `X-User` | 门户用户名（可改名） |
| `X-Role` | 该用户**在本站**的角色：`user` 或 `admin` |
| `X-Portal-Sub` | 稳定用户 id，改名不变；本地数据用它关联 |
| `X-Portal-Anon` | 值 `1`：允许匿名访问的站点上的匿名访客。与上面三个头二选一，门卫不会同时发送 |

- **已登录**：`X-User` 与 `X-Portal-Sub` 都非空；`X-Role` 缺省或非法时按 `user`。缺任何一个都视为未认证。
- **匿名访客**（`X-Portal-Anon: 1`、无身份头）没有身份：身份函数返回 `None` / `null`，`require_identity` 照旧 401；用 `is_anonymous` / `isAnonymous` 区分「匿名」与「没经过门卫」。两类头同时到达时身份优先（匿名为假）。
- **绕过门卫的请求**（带 `Authorization` 头、健康端点、排除路径）两类头都没有，应用只认自己的 token。

安全前提：

- 应用容器**只能经 Caddy 访问**（不发布端口）。任何绕过 Caddy 直连应用的路径都会让头伪造成为可能。
- 门卫对**每一个**到达应用的请求先剥掉客户端自带的 `X-User` / `X-Role` / `X-Portal-Sub` / `X-Portal-Anon`，再由 `forward_auth` 写入真实值。没有这一步，任何人带上 `Authorization: x` 和伪造的 `X-User: admin` 就能冒充管理员。

### Python（`szyyw_auth`）

| 名称 | 说明 |
|---|---|
| `Identity(user, role, sub)` | 冻结 dataclass，`.is_admin` |
| `identity_from_headers(get)` | 由 `name → value` 取头函数构造 `Identity` 或 `None`（不看 `SZYYW_SSO`） |
| `is_anonymous(get)` | 匿名访客判定 |
| `sso_enabled()` | `SZYYW_SSO` 为 `1/true/yes/on` |
| `login_url(portal, return_to)` | 门户登录地址 |
| `HEADER_USER` / `HEADER_ROLE` / `HEADER_SUB` / `HEADER_ANON`、`ROLES` | 常量 |
| `szyyw_auth.flask` | `current_identity()`、`is_anonymous()`、`@optional_identity`（设 `g.identity`）、`@require_identity(role=None)` |
| `szyyw_auth.starlette` | `current_identity(request)`、`is_anonymous(request)`；依赖 `optional_identity`、`require_identity`（401）、`require_admin`（401 / 403） |

适配器在 SSO 关闭时一律返回 `None` / `False`。

### JS（`@szyyw/auth`）

| 导出 | 说明 |
|---|---|
| `@szyyw/auth` | `identityFromHeaders(get)` → `{ user, role, sub, isAdmin }` 或 `null`；`isAnonymousFromHeaders(get)`；`ssoEnabled()`；`loginUrl(portal, returnTo)`；`HEADERS`；`VERSION` |
| `@szyyw/auth/express` | `identity(req)`、`isAnonymous(req)`、`optionalIdentity()`（设 `req.identity`，不拒绝）、`requireIdentity(role?)`（401 `{error:'unauthorized'}` / 403 `{error:'forbidden'}`） |
| `@szyyw/auth/next` | `identityFromRequestHeaders(headers)`、`optionalIdentity`（同一函数的别名）、`isAnonymousFromRequestHeaders(headers)`；接受 `next/headers` 的 `headers()` 或任意 Fetch `Headers` |

类型声明见各 `.d.ts`。

## 开发

```bash
npm test                                   # node --test test/*.test.js
cd python && python -m pytest tests -q
```

## 许可

MIT，见 [LICENSE](LICENSE)。
