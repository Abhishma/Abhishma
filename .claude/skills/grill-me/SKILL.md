---
name: grill-me
description: Interview the user with clarifying questions before starting a non-trivial build/implementation task. Use when the user asks to build, create, implement, or design something with real scope or open design decisions — not for small, unambiguous fixes.
---

# Grill Me

Force clarification before building, so effort isn't wasted on the wrong thing.

## When to trigger

Trigger on requests like "build X", "create Y", "implement Z", "design a system for..." when the task has multiple plausible interpretations, unstated scope, or nontrivial architecture/design decisions.

Do **not** trigger for: one-line bug fixes, requests with an exact spec already given, trivial changes that follow an existing pattern in the codebase, or when the user has explicitly said "just build it" / "skip the questions".

## Process

1. Before writing any code, plan, or document, ask 10-15 questions covering as many of these as are actually unresolved:
   - Goal and what "done" looks like / success criteria
   - Target users / audience
   - Explicit scope boundaries — what's *out* of scope
   - Constraints (stack, tools, deadline, budget, existing conventions to follow)
   - Edge cases and failure modes that matter
   - Data sources / inputs and their shape
   - Non-functional requirements (performance, security, scale) if relevant
   - How it will be validated or tested
2. Use the structured question tool where options are enumerable (multiple choice); ask open-ended items directly in text. Don't pad the list to hit a number — ask fewer if fewer genuinely apply, but don't skip categories that are actually ambiguous.
3. Do not start implementation until the essential unknowns are resolved.
4. After getting answers, restate your understanding in a few tight bullets before building, so the user can correct you cheaply before real work starts.
