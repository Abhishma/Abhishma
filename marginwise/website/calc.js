// Marginwise calculator formulas. Pure functions, no DOM, shared by the page and the tests.
// Every default that comes from a study is labelled with its source on the page; all inputs are editable.
(function (root) {
  const pos = (v) => (Number.isFinite(v) && v > 0 ? v : 0);

  // Performance marketing: profit after ads and break-even ROAS.
  function profitAfterAds({ spend, roas, aov, cogsPct, feePct, returnsPct, fulfilPerOrder, overAttribPct }) {
    const trueRevenue = spend * roas * (1 - overAttribPct / 100);
    const orders = aov > 0 ? trueRevenue / aov : 0;
    const contribution = aov * (1 - (returnsPct + cogsPct + feePct) / 100) - fulfilPerOrder;
    const profit = orders * contribution - spend;
    const breakEvenRoas = contribution > 0 ? aov / (contribution * (1 - overAttribPct / 100)) : Infinity;
    return { trueRevenue, orders, contribution, profit, breakEvenRoas };
  }

  // CRO: revenue and margin from a conversion lift.
  function conversionLift({ sessions, crPct, aov, marginPct, liftPct }) {
    const orders = sessions * crPct / 100;
    const revenue = orders * aov;
    const extraRevenue = revenue * liftPct / 100;
    return { orders, revenue, extraRevenue, extraMarginYear: extraRevenue * marginPct / 100 * 12, newCrPct: crPct * (1 + liftPct / 100) };
  }

  // Website speed: revenue at stake per 0.1 s at the study rate (8.4% per 0.1 s, Deloitte/Google 2020), linear scenario.
  function speedValue({ sessions, crPct, aov, marginPct, tenths, ratePerTenthPct = 8.4 }) {
    const revenue = sessions * crPct / 100 * aov;
    const perTenth = revenue * ratePerTenthPct / 100;
    const scenario = perTenth * pos(tenths);
    return { revenue, perTenth, scenario, scenarioMarginYear: scenario * marginPct / 100 * 12 };
  }

  // SEO, AEO and GEO: what organic and AI-referred traffic is worth, and what it would cost to buy.
  function searchValue({ sessions, crPct, aov, marginPct, cpc }) {
    const revenue = sessions * crPct / 100 * aov;
    return { revenue, margin: revenue * marginPct / 100, adCostEquivalent: sessions * cpc };
  }

  // AI support agent: tickets resolved without a person.
  function supportAgent({ tickets, automatablePct, resolvePct, costPerTicket, minutesPerTicket, fee }) {
    const resolved = tickets * automatablePct / 100 * resolvePct / 100;
    return { resolved, hours: resolved * minutesPerTicket / 60, saving: resolved * costPerTicket - fee };
  }

  // AI phone receptionist: jobs won back from calls nobody answered.
  function receptionist({ calls, answeredPct, aiAnsweredPct, bookPct, jobValue, marginPct, fee }) {
    const extraAnswered = calls * pos(aiAnsweredPct - answeredPct) / 100;
    const jobs = extraAnswered * bookPct / 100;
    return { extraAnswered, jobs, revenue: jobs * jobValue, profit: jobs * jobValue * marginPct / 100 - fee };
  }

  // ERP sync and payout reconciliation: manual hours and errors removed.
  function opsAutomation({ hours, hourlyCost, automatePct, errors, costPerError, fee }) {
    const hoursSaved = hours * automatePct / 100;
    const errorsAvoided = errors * automatePct / 100;
    return { hoursSaved, errorsAvoided, saving: hoursSaved * hourlyCost + errorsAvoided * costPerError - fee };
  }

  // Australian surcharge ban (1 Oct 2026): what the surcharge used to recover, and the options.
  function surchargeBan({ cardRevenue, surchargePct, cardFeePct, cheaperFeePct, shiftPct }) {
    const lostSurcharge = cardRevenue * surchargePct / 100;
    const cardFees = cardRevenue * cardFeePct / 100;
    const shiftSaving = cardRevenue * shiftPct / 100 * pos(cardFeePct - cheaperFeePct) / 100;
    // Before the ban the shopper paid P x (1 + s) and the card fee applied to that total.
    // Keeping the same net after fees therefore needs a price rise equal to the surcharge rate.
    return { lostSurcharge, lostYear: lostSurcharge * 12, cardFees, shiftSaving, priceRisePct: surchargePct };
  }

  // Tariff landed cost: unit landed cost, margin and the price needed for a target margin.
  function landedCost({ unitCost, freight, dutyPct, tariffPct, otherFees, price, targetMarginPct }) {
    const duties = unitCost * (dutyPct + tariffPct) / 100;
    const landed = unitCost + freight + duties + otherFees;
    const marginPct = price > 0 ? (price - landed) / price * 100 : 0;
    const priceForTarget = targetMarginPct < 100 ? landed / (1 - targetMarginPct / 100) : Infinity;
    return { duties, landed, marginPct, priceForTarget };
  }

  // India COD and RTO: cost of cash-on-delivery orders that return to origin, and the saving from shifting to prepaid.
  function codRto({ orders, codPct, codRtoPct, prepaidRtoPct, rtoCost, shiftPct }) {
    const codOrders = orders * codPct / 100;
    const rtoNow = codOrders * codRtoPct / 100 + (orders - codOrders) * prepaidRtoPct / 100;
    const shifted = codOrders * shiftPct / 100;
    const rtoAfter = (codOrders - shifted) * codRtoPct / 100 + (orders - codOrders + shifted) * prepaidRtoPct / 100;
    return { rtoNow, costNow: rtoNow * rtoCost, rtoAfter, saving: (rtoNow - rtoAfter) * rtoCost };
  }

  const api = { profitAfterAds, conversionLift, speedValue, searchValue, supportAgent, receptionist, opsAutomation, surchargeBan, landedCost, codRto };
  if (typeof module !== "undefined") module.exports = api; else root.MWCalc = api;
})(this);
