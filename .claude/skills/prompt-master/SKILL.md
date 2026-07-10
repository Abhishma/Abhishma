---
name: prompt-master
description: Restructure a messy, stream-of-consciousness brain-dump into a clear, structured brief before executing it. Use when the user pastes a long rambling request, voice-to-text dump, or unstructured notes and wants it turned into an actionable task.
---

# Prompt Master

Turn a brain-dump into a brief the task can actually be executed against.

## Process

1. Read the raw dump and identify: the actual underlying goal, context/background the user assumed but didn't state, constraints, and anything contradictory, circular, or missing.
2. Reorganize into a structured brief with these sections (omit any that are genuinely empty — don't pad):
   - **Goal** — what success looks like, in one or two sentences
   - **Context** — relevant background the request implied
   - **Constraints** — tools, stack, deadline, format, tone, or other hard requirements
   - **Requirements** — explicit, concrete asks extracted from the dump
   - **Open questions** — contradictions or critical gaps that need an answer before proceeding
   - **Suggested first step**
3. If there are contradictions (e.g. two mutually exclusive asks) or a critical unstated gap, surface them explicitly as open questions — do not silently pick one interpretation and move on.
4. Show the restructured brief to the user before executing against it, unless they've explicitly said to just proceed.
5. Keep the brief tight: no restating the same point twice, no filler sections.
