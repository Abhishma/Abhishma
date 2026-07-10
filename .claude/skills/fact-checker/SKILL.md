---
name: fact-checker
description: Verify every factual claim in a piece of text against live sources before publishing, citing a source for each claim. Use when the user asks to fact-check or verify content, or is about to publish text containing stats, dates, names, quotes, or "studies show"-type claims.
---

# Fact Checker

Every claim gets a citation or gets flagged — nothing passes silently.

## Process

1. Extract every checkable factual claim from the text: numbers/stats, dates, names, quotes, causal claims, "studies show" / "research indicates" statements, and any claim about a specific company, product, or event.
2. For each claim, search for a credible source (prefer WebSearch/WebFetch over memory — never verify from training-data recall alone, since it can be stale or wrong). Prefer primary sources (original studies, official docs, filings, primary reporting) over secondary summaries or blogs that may have already distorted the claim.
3. If the text already contains a citation, verify the citation actually supports the claim as stated — citations are frequently misquoted or overstated, so check the source, don't just trust its presence.
4. Classify each claim:
   - ✅ **Verified** — cite the exact source URL.
   - ⚠️ **Partially correct / outdated / needs nuance** — explain what's wrong and cite the correcting source.
   - ❌ **False or unsupported** — explain why and cite the contradicting source.
   - ❓ **Unverifiable** — state this explicitly rather than guessing or letting it slide.
5. Produce a claim-by-claim report with a citation attached to every claim. A claim with no findable citation does not get published as-is — flag it for removal or softening (e.g. "reportedly" / hedged) rather than asserting it.
6. Do not rewrite or improve the prose unless asked — this skill's job is verification, not editing.
