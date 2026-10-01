export const VERSION: string;
export const HEADERS: { user: string; role: string; sub: string };
export interface Identity { user: string; role: 'user' | 'admin'; sub: string; isAdmin: boolean }
/** True when SZYYW_SSO is 1/true/yes/on. */
export function ssoEnabled(): boolean;
/** null when the request did not come through the gate. */
export function identityFromHeaders(get: (name: string) => string | null | undefined): Identity | null;
export function loginUrl(portal: string, returnTo: string): string;
