import { identityFromHeaders, ssoEnabled } from './index.js';

/** Works with `headers()` from next/headers and any Fetch `Headers`. null when SSO is off or no gate identity. */
export function identityFromRequestHeaders(headers) {
  if (!ssoEnabled()) return null;
  return identityFromHeaders((n) => headers.get(n));
}
