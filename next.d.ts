import type { Identity } from './index.js';
export function identityFromRequestHeaders(headers: { get(name: string): string | null }): Identity | null;
