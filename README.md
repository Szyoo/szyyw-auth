# szyyw-auth

`*.szyyw.xyz` 各应用的 **SSO 客户端**：读 Caddy 门卫注入的身份头，几十行，Python 和 JS 各一份。

## 契约

浏览器 → Caddy `forward_auth` → portal `/api/auth/verify`。只有 **portal 会话有效且该用户对本站有权限** 时请求才会到达应用，并带上：

| 头 | 含义 |
|---|---|
| `X-User` | portal 用户名 |
| `X-Role` | 该用户**在本站**的角色：`user` 或 `admin`（由 portal 的权限矩阵决定） |
| `X-Portal-Sub` | 稳定主体标识（目前 = 用户名，预留） |

**安全前提**：这些头可信，仅因为应用容器**只有 Caddy 能访问**（compose 里没有 `ports:`，只挂 `ingress` 网络）。任何能绕过 Caddy 直连应用的路径都会让头伪造成为可能——不要给应用发布端口。

**门卫侧的义务**（契约的另一半，在 `szyyw-platform` 的 Caddyfile `(sso)` 片段里实现）：对**每一个**到达应用的请求先剥掉客户端自带的 `X-User` / `X-Role` / `X-Portal-Sub`，再由 `forward_auth` 给受门卫的请求写入真实值。绕过门卫的请求（带 `Authorization`、健康端点、机器路径）因此到达应用时**没有**身份头——应用对它们只认自己的 token。没有这一步，任何人用 `-H 'Authorization: x' -H 'X-User: admin'` 就能冒充管理员。

**开关**：`SZYYW_SSO=1` 才启用。未设置时所有函数返回 `None`/拒绝，本地开发继续用应用自己的登录。

**机器端点**（cron、agent、webhook、推送）不走门卫：Caddy 对带 `Authorization` 头或在排除路径上的请求直接放行，应用照旧自己验 token。

## 安装

```bash
# Python（Flask / FastAPI / Starlette）
pip install "szyyw-auth @ git+https://github.com/Szyoo/szyyw-auth@v0.1.0#subdirectory=python"

# JS（Express / Next）——用 codeload tarball，node:alpine 里没有 git
npm i "https://codeload.github.com/Szyoo/szyyw-auth/tar.gz/refs/tags/v0.1.0"
```

## 用法

```python
# Flask
from szyyw_auth.flask import current_identity, require_identity

@app.get("/me")
@require_identity()            # 401 没身份；require_identity("admin") 则非 admin 403
def me():
    ident = current_identity()
    return {"user": ident.user, "role": ident.role}
```

```python
# FastAPI
from fastapi import Depends
from szyyw_auth import Identity
from szyyw_auth.starlette import require_identity, require_admin

@app.get("/me")
def me(ident: Identity = Depends(require_identity)): ...
```

```js
// Express
import { requireIdentity } from '@szyyw/auth/express';
app.get('/api/me', requireIdentity(), (req, res) => res.json(req.identity));

// Next (route handler / server component)
import { headers } from 'next/headers';
import { identityFromRequestHeaders } from '@szyyw/auth/next';
const ident = identityFromRequestHeaders(await headers());   // null → treat as logged out
```

未登录的浏览器导航该去哪：`login_url(portal, return_to)` / `loginUrl(portal, returnTo)` 生成 portal 登录地址（带 `?rd=`，登完跳回）。正常情况下门卫已经替你跳了；这个只在应用自己的回退逻辑里用。

## 接入一个应用的典型改动

1. 读 `X-User` 代替自己的 session 查用户（多用户应用：按 `X-User` 查本地映射表）。
2. 自己的 `login_required` 换成 `require_identity`；登录页在 `SZYYW_SSO=1` 时 302 到 portal。
3. 机器端点保持原样（Bearer token）。
4. 仍然要能在 `SZYYW_SSO` 未设时跑——本地开发和门卫未开时都靠它。

## 版本

与 [szyyw-design](https://github.com/Szyoo/szyyw-design)、[claude-bridge](https://github.com/Szyoo/claude-bridge) 同一套：semver tag 分发，消费方 pin 精确 tag，见 `CHANGELOG.md`。
