import type { Identity } from './index.js';
export function identityFromRequestHeaders(headers: { get(name: string): string | null }): Identity | null;
export function optionalIdentity(headers: { get(name: string): string | null }): Identity | null;
export function isAnonymousFromRequestHeaders(headers: { get(name: string): string | null }): boolean;
