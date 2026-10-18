import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const C = createRequire(import.meta.url)('./calc.js');
const near = (a, b, d = 0.01) => assert.ok(Math.abs(a - b) <= d, `${a} != ${b}`);

test('profit after ads', () => {
  const r = C.profitAfterAds({ spend: 10000, roas: 3, aov: 100, cogsPct: 35, feePct: 3, returnsPct: 8, fulfilPerOrder: 12, overAttribPct: 20 });
  near(r.trueRevenue, 24000); near(r.orders, 240); near(r.contribution, 42); near(r.profit, 80); near(r.breakEvenRoas, 2.976);
});
test('profit after ads: negative contribution gives infinite break-even', () => {
  assert.equal(C.profitAfterAds({ spend: 100, roas: 2, aov: 50, cogsPct: 80, feePct: 3, returnsPct: 10, fulfilPerOrder: 10, overAttribPct: 0 }).breakEvenRoas, Infinity);
});
test('conversion lift', () => {
  const r = C.conversionLift({ sessions: 40000, crPct: 1.8, aov: 110, marginPct: 60, liftPct: 20 });
  near(r.orders, 720); near(r.revenue, 79200); near(r.extraRevenue, 15840); near(r.extraMarginYear, 114048); near(r.newCrPct, 2.16);
});
test('speed value', () => {
  const r = C.speedValue({ sessions: 40000, crPct: 2, aov: 75, marginPct: 60, tenths: 3 });
  near(r.revenue, 60000); near(r.perTenth, 5040); near(r.scenario, 15120); near(r.scenarioMarginYear, 108864);
});
test('search value', () => {
  const r = C.searchValue({ sessions: 20000, crPct: 1.5, aov: 80, marginPct: 50, cpc: 1.5 });
  near(r.revenue, 24000); near(r.margin, 12000); near(r.adCostEquivalent, 30000);
});
test('support agent', () => {
  const r = C.supportAgent({ tickets: 3000, automatablePct: 40, resolvePct: 60, costPerTicket: 5, minutesPerTicket: 6, fee: 750 });
  near(r.resolved, 720); near(r.hours, 72); near(r.saving, 2850);
});
test('receptionist', () => {
  const r = C.receptionist({ calls: 400, answeredPct: 52, aiAnsweredPct: 95, bookPct: 43, jobValue: 450, marginPct: 50, fee: 600 });
  near(r.extraAnswered, 172); near(r.jobs, 73.96); near(r.revenue, 33282); near(r.profit, 16041);
});
test('receptionist: AI rate below current answer rate adds nothing', () => {
  near(C.receptionist({ calls: 100, answeredPct: 90, aiAnsweredPct: 80, bookPct: 50, jobValue: 100, marginPct: 50, fee: 0 }).jobs, 0);
});
test('ops automation', () => {
  const r = C.opsAutomation({ hours: 40, hourlyCost: 35, automatePct: 70, errors: 10, costPerError: 60, fee: 900 });
  near(r.hoursSaved, 28); near(r.errorsAvoided, 7); near(r.saving, 500);
});
test('surcharge ban', () => {
  const r = C.surchargeBan({ cardRevenue: 200000, surchargePct: 1.5, cardFeePct: 1.4, cheaperFeePct: 0.5, shiftPct: 30 });
  near(r.lostSurcharge, 3000); near(r.lostYear, 36000); near(r.cardFees, 2800); near(r.shiftSaving, 540); near(r.priceRisePct, 1.5);
});
test('landed cost', () => {
  const r = C.landedCost({ unitCost: 20, freight: 2, dutyPct: 5, tariffPct: 10, otherFees: 0, price: 60, targetMarginPct: 60 });
  near(r.duties, 3); near(r.landed, 25); near(r.marginPct, 58.333); near(r.priceForTarget, 62.5);
});
test('COD and RTO', () => {
  const r = C.codRto({ orders: 5000, codPct: 60, codRtoPct: 26, prepaidRtoPct: 2, rtoCost: 120, shiftPct: 25 });
  near(r.rtoNow, 820); near(r.costNow, 98400); near(r.rtoAfter, 640); near(r.saving, 21600);
});
