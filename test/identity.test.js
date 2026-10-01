import test from 'node:test';
import assert from 'node:assert/strict';
import { identityFromHeaders, isAnonymousFromHeaders } from '../index.js';
import * as ex from '../express.js';
import * as nx from '../next.js';

const mk = (h) => { const l = Object.fromEntries(Object.entries(h).map(([k, v]) => [k.toLowerCase(), v])); return (n) => l[n.toLowerCase()] ?? null; };
const req = (h) => ({ get: mk(h) });
const hdrs = (h) => ({ get: mk(h) });
const FULL = { 'X-User': 'alice', 'X-Role': 'admin', 'X-Portal-Sub': 'u1' };
const ANON = { 'X-Portal-Anon': '1' };
const run = (mw, r) => { const out = { next: false }; const res = { status(c) { out.status = c; return this; }, json(b) { out.body = b; return this; } }; mw(r, res, () => { out.next = true; }); return out; };

test.beforeEach(() => { process.env.SZYYW_SSO = '1'; });
test.after(() => { delete process.env.SZYYW_SSO; });

test('full headers -> identity', () => {
  assert.deepEqual(identityFromHeaders(mk(FULL)), { user: 'alice', role: 'admin', sub: 'u1', isAdmin: true });
});
test('role defaults to user', () => {
  assert.equal(identityFromHeaders(mk({ 'X-User': 'a', 'X-Portal-Sub': 's' })).role, 'user');
});
test('X-User without sub -> null (0.2.0 behaviour change)', () => {
  assert.equal(identityFromHeaders(mk({ 'X-User': 'alice' })), null);
  assert.equal(identityFromHeaders(mk({ 'X-User': 'alice', 'X-Portal-Sub': '  ' })), null);
});
test('anon header -> null identity, anonymous true', () => {
  assert.equal(identityFromHeaders(mk(ANON)), null);
  assert.equal(isAnonymousFromHeaders(mk(ANON)), true);
  assert.equal(ex.isAnonymous(req(ANON)), true);
  assert.equal(ex.identity(req(ANON)), null);
  assert.equal(nx.isAnonymousFromRequestHeaders(hdrs(ANON)), true);
  assert.equal(nx.optionalIdentity(hdrs(ANON)), null);
});
test('anon value other than 1, or no headers -> not anonymous', () => {
  assert.equal(isAnonymousFromHeaders(mk({ 'X-Portal-Anon': '0' })), false);
  assert.equal(isAnonymousFromHeaders(mk({})), false);
});
test('anon + identity together -> identity wins', () => {
  const h = { ...FULL, ...ANON };
  assert.equal(identityFromHeaders(mk(h)).user, 'alice');
  assert.equal(isAnonymousFromHeaders(mk(h)), false);
});
test('requireIdentity: anonymous -> 401', () => {
  const o = run(ex.requireIdentity(), req(ANON));
  assert.equal(o.status, 401); assert.equal(o.next, false);
});
test('requireIdentity: identity passes; admin gate 403 for user', () => {
  assert.equal(run(ex.requireIdentity(), req(FULL)).next, true);
  const o = run(ex.requireIdentity('admin'), req({ ...FULL, 'X-Role': 'user' }));
  assert.equal(o.status, 403);
});
test('optionalIdentity: passes null for anonymous, identity otherwise', () => {
  const r1 = req(ANON); const o1 = run(ex.optionalIdentity(), r1);
  assert.equal(o1.next, true); assert.equal(r1.identity, null);
  const r2 = req(FULL); run(ex.optionalIdentity(), r2);
  assert.equal(r2.identity.user, 'alice');
  assert.equal(nx.optionalIdentity(hdrs(FULL)).sub, 'u1');
});
test('SSO off -> everything null/false', () => {
  delete process.env.SZYYW_SSO;
  assert.equal(ex.identity(req(FULL)), null);
  assert.equal(ex.isAnonymous(req(ANON)), false);
  assert.equal(nx.identityFromRequestHeaders(hdrs(FULL)), null);
});
