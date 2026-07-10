# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is `Abhishma/Abhishma` — the special GitHub "profile README" repository. A repo named identically to the account username is rendered by GitHub as the content of the user's public profile page (github.com/Abhishma). There is no application code here.

The repository currently contains a single file, `README.md`, which is a **drafting/notes document** for that profile page rather than the final rendered copy. It mixes several distinct kinds of content that should not be conflated:

- **Recommended profile headline** — a one-line tagline suggestion for the GitHub bio field (not part of the profile README body).
- **Short bio** — candidate prose for a profile "About" section.
- **Profile README opening** — the actual draft copy intended to appear at the top of the rendered profile page.
- **Suggested pinned order** — a list of *other, separate repositories* (`relevance-medic`, `roadmap-linter`, `returncraft`, `experiment-skeptic`, `launch-gatekeeper`) that the user intends to pin on their profile. These repos do not live in this repository and are not accessible from here.
- **Suggested contribution note** — draft copy for a "how to reach me" / collaboration blurb.
- **Operational tooling** — a link to another external repo (`shopify-image-pipeline`).

When editing `README.md`, preserve this section structure (`##` headings) since it distinguishes "meta suggestions" (headline, pinned order) from "content meant to be pasted verbatim" (profile README opening, bio, contribution note). Don't merge them into a single flat block of prose.

## Development workflow

There is no build, lint, or test tooling in this repository — it is a single Markdown file with no code, package manifest, or CI configuration. Changes are just edits to `README.md`; there is nothing to compile or run.

## Content/voice conventions

The recurring theme across the referenced portfolio repos (and the framing to keep consistent if extending this content) is: *"AI is most useful when it reduces ambiguity, surfaces evidence, and stops before it lies."* Draft copy favors bounded, auditable systems with explicit trust boundaries, abstention logic, and human-in-the-loop review over open-ended "AI agent" framing — keep new copy in that register rather than generic AI-hype language.
