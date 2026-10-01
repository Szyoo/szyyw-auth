/* @szyyw/auth · index.js
   The szyyw.xyz Caddy gate (forward_auth → portal /api/auth/verify) only lets a
   request through when the portal session is valid and the user may open this
   site, then injects X-User / X-Role / X-Portal-Sub (or X-Portal-Anon: 1 for an anonymous visitor on a
   site that allows anonymous access). Those headers are
   trustworthy ONLY because the app container is reachable solely via Caddy
   (no published ports). Enable with SZYYW_SSO=1; unset = everything returns
   null so local dev keeps the app's own login. */

export const VERSION = '0.2.0';
export const HEADERS = { user: 'x-user', role: 'x-role', sub: 'x-portal-sub', anon: 'x-portal-anon' };
const ROLES = ['user', 'admin'];

export const ssoEnabled = () =>
  ['1', 'true', 'yes', 'on'].includes(String(process.env.SZYYW_SSO ?? '').trim().toLowerCase());

/** Build an identity from a header getter (name → value | null). null = did not come through the gate. */
export function identityFromHeaders(get) {
  const user = (get(HEADERS.user) || '').trim();
  const sub = (get(HEADERS.sub) || '').trim();
  if (!user || !sub) return null; // identity needs BOTH X-User and X-Portal-Sub
  let role = (get(HEADERS.role) || 'user').trim().toLowerCase();
  if (!ROLES.includes(role)) role = 'user';
  return { user, role, sub, isAdmin: role === 'admin' };
}

/** True for an anonymous visitor (X-Portal-Anon: 1, no identity). Identity wins if both arrive. */
export function isAnonymousFromHeaders(get) {
  if (identityFromHeaders(get)) return false;
  return (get(HEADERS.anon) || '').trim() === '1';
}

/** Where to send an unauthenticated browser: portal login that returns to `returnTo`. */
export const loginUrl = (portal, returnTo) =>
  `${portal.replace(/\/$/, '')}/login?rd=${encodeURIComponent(returnTo)}`;
