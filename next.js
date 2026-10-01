import { identityFromHeaders, isAnonymousFromHeaders, ssoEnabled } from './index.js';

/** Works with `headers()` from next/headers and any Fetch `Headers`. null when SSO is off, anonymous, or no gate identity. */
export function identityFromRequestHeaders(headers) {
  if (!ssoEnabled()) return null;
  return identityFromHeaders((n) => headers.get(n));
}

/** Identity or null, never rejects (same as identityFromRequestHeaders, explicit "optional" intent). */
export const optionalIdentity = identityFromRequestHeaders;

/** True for an anonymous visitor (X-Portal-Anon: 1, no identity). False when SSO is off. */
export function isAnonymousFromRequestHeaders(headers) {
  return ssoEnabled() && isAnonymousFromHeaders((n) => headers.get(n));
}
