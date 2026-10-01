export const VERSION: string;
export const HEADERS: { user: string; role: string; sub: string; anon: string };
export interface Identity { user: string; role: 'user' | 'admin'; sub: string; isAdmin: boolean }
/** True when SZYYW_SSO is 1/true/yes/on. */
export function ssoEnabled(): boolean;
/** null when the request did not come through the gate. */
export function identityFromHeaders(get: (name: string) => string | null | undefined): Identity | null;
export function loginUrl(portal: string, returnTo: string): string;
/** true for an anonymous visitor: X-Portal-Anon: 1 and no identity (identity wins if both). */
export function isAnonymousFromHeaders(get: (name: string) => string | null | undefined): boolean;
