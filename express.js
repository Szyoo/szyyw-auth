import { identityFromHeaders, ssoEnabled } from './index.js';

/** Identity for an Express request, or null (SSO off / bypassed the gate). */
export const identity = (req) => (ssoEnabled() ? identityFromHeaders((n) => req.get(n)) : null);

/** Middleware: 401 without a gate identity, 403 if role 'admin' is required but missing. Sets req.identity. */
export const requireIdentity = (role) => (req, res, next) => {
  const id = identity(req);
  if (!id) return res.status(401).json({ error: 'unauthorized' });
  if (role === 'admin' && !id.isAdmin) return res.status(403).json({ error: 'forbidden' });
  req.identity = id;
  next();
};
