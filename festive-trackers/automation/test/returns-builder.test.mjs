import { test } from 'node:test';
import assert from 'node:assert/strict';
import { planLines, planOrders, build, KINDS } from '../returns-builder.mjs';

const D = '2026-10-02';
const table = (cols, rows) => ({ columns: cols.map(name => ({ name })), rows });
// 10:15 IST = 04:45 UTC; 18:40 IST = 13:10 UTC
const LINES = table(['hour', 'order_name', 'product_variant_sku', 'product_title', 'quantity_returned', 'returns'], [
  ['2026-10-02T04:45:00Z', '#1001', 'SKU-A', 'Oversized Tee', -2, -1598],
  ['2026-10-02T04:50:00Z', '#1002', 'SKU-A', 'Oversized Tee', -1, -799],
  ['2026-10-02T13:10:00Z', '#1003', 'SKU-B', 'Baggy Jeans', -1, -1699],
  ['2026-10-02T13:20:00Z', '#1004', 'SKU-C', 'Hoodie', -1, -1499],
  ['2026-10-02T13:30:00Z', '#1005', '', 'Gift wrap', 0, 0],
]);
const ORDERS = { data: { orders: { nodes: [
  { name: '#1001', tags: ['cancel-customer_changed_mind', 'Cancelled'], cancelReason: 'CUSTOMER', refunds: [{ note: 'Order cancelled', createdAt: D, refundLineItems: { nodes: [{ lineItem: { sku: 'SKU-A' } }] } }] },
  { name: '#1002', tags: ['RTO-Delivered'], refunds: [{ note: 'RTO - customer declined delivery', createdAt: D, refundLineItems: { nodes: [{ lineItem: { sku: 'SKU-A' } }] } }] },
  { name: '#1003', tags: ['Return'], refunds: [{ note: 'Customer returned the product: size too small', createdAt: D, refundLineItems: { nodes: [{ lineItem: { sku: 'SKU-B' } }] } }] },
  { name: '#1004', tags: [], refunds: [{ note: 'Marked lost by courier', createdAt: D, refundLineItems: { nodes: [{ lineItem: { sku: 'SKU-C' } }] } }] },
] } } };

test('three passes build the store-wide returns record', () => {
  const lineCalls = planLines([D]);
  assert.equal(lineCalls.length, 1);
  assert.match(lineCalls[0].input.query, /TIMESERIES hour HAVING quantity_returned != 0 SINCE 2026-10-02 UNTIL 2026-10-02/);
  const responses = { [lineCalls[0].id]: LINES };
  const orderCalls = planOrders(responses, [D]);
  assert.equal(orderCalls.length, 1);
  assert.equal(orderCalls[0].tool, 'graphql_query');
  assert.equal(orderCalls[0].input.variables.q, 'name:1001 OR name:1002 OR name:1003 OR name:1004');
  responses[orderCalls[0].id] = ORDERS;

  const [w] = build(responses, [D], { now: 1 });
  assert.equal(w.collection, 'returns'); assert.equal(w.doc_id, D);
  const byKind = Object.fromEntries(KINDS.map(k => [k, w.data.rows.filter(r => r[2] === k).reduce((s, r) => s + r[4], 0)]));
  assert.deepEqual(byKind, { 'Customer return': 1, 'RTO (not delivered)': 1, Cancelled: 2, 'Other refund': 1 });
  const cancel = w.data.rows.find(r => r[2] === 'Cancelled');
  assert.deepEqual(cancel.slice(0, 7), ['SKU-A', 'Oversized Tee', 'Cancelled', 'Customer changed mind', 2, 1598, ['#1001']]);
  assert.deepEqual(cancel[7], { 10: [2, 1598] });
  // hourly totals the D0 view reads: [units, value, orders] per IST hour
  assert.deepEqual(w.data.hrs.All[10], [3, 2397, 2]);
  assert.deepEqual(w.data.hrs.All[18], [2, 3198, 2]);
  assert.deepEqual(w.data.hrs['Customer return'][18], [1, 1699, 1]);
  assert.equal(w.data.rows.some(r => r[1] === 'Gift wrap'), false, 'zero-quantity rows dropped');
});

test('a missing response stops the build', () => {
  assert.throws(() => build({}, [D]), /Missing response/);
});
