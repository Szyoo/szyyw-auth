import { identityFromHeaders, isAnonymousFromHeaders, ssoEnabled } from './index.js';

/** Identity for an Express request, or null (SSO off / anonymous / bypassed the gate). */
export const identity = (req) => (ssoEnabled() ? identityFromHeaders((n) => req.get(n)) : null);

/** True for an anonymous visitor (X-Portal-Anon: 1, no identity). False when SSO is off. */
export const isAnonymous = (req) => ssoEnabled() && isAnonymousFromHeaders((n) => req.get(n));

/** Middleware: never rejects. Sets req.identity to the identity or null. */
export const optionalIdentity = () => (req, res, next) => {
  req.identity = identity(req);
  next();
};

/** Middleware: 401 without a gate identity (anonymous included), 403 if role 'admin' is required but missing. Sets req.identity. */
export const requireIdentity = (role) => (req, res, next) => {
  const id = identity(req);
  if (!id) return res.status(401).json({ error: 'unauthorized' });
  if (role === 'admin' && !id.isAdmin) return res.status(403).json({ error: 'forbidden' });
  req.identity = id;
  next();
};
