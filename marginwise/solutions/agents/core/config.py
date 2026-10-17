"""Runtime configuration for the Marginwise agent runner.

Everything can be overridden with environment variables so that the same code
runs in tests (offline, FakeClient) and in production (Anthropic Messages API).
"""

from __future__ import annotations

import os

# Main reasoning / tool-use model.
DEFAULT_MODEL = os.getenv("MARGINWISE_MODEL", "claude-sonnet-5-5")

# Cheap model for classification, routing and short summaries.
CLASSIFY_MODEL = os.getenv("MARGINWISE_CLASSIFY_MODEL", "claude-haiku-5-5")

# Hard cap on model calls per run. A "turn" is one Messages API request.
DEFAULT_MAX_TURNS = int(os.getenv("MARGINWISE_MAX_TURNS", "10"))

DEFAULT_MAX_TOKENS = int(os.getenv("MARGINWISE_MAX_TOKENS", "8000"))

# Server-side refusal fallback (Claude API only). When enabled, real requests go
# through client.beta.messages.create with the fallback beta so a safety
# refusal on the primary model is retried server-side on a suitable model.
# Off by default: confirm the beta name in the current Anthropic docs, then set
# MARGINWISE_SERVER_FALLBACKS=1 to enable. Leave off on Bedrock/Vertex.
SERVER_FALLBACKS = os.getenv("MARGINWISE_SERVER_FALLBACKS", "0") not in ("0", "false", "False")
SERVER_FALLBACK_BETA = "server-side-fallback-2026-07-01"

# Where JSON transcripts are written when a run does not pass transcript_dir.
TRANSCRIPT_DIR = os.getenv("MARGINWISE_TRANSCRIPT_DIR", "")
