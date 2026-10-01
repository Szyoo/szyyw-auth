import type { Identity } from './index.js';
export function identity(req: { get(name: string): string | undefined }): Identity | null;
export function requireIdentity(role?: 'admin'): (req: any, res: any, next: () => void) => void;
