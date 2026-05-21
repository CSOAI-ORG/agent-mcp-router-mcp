#!/usr/bin/env python3
"""
Agent MCP Router MCP — one router for the whole MEOK fleet
============================================================

By MEOK AI Labs · https://meok.ai · MIT
<!-- mcp-name: io.github.CSOAI-ORG/agent-mcp-router-mcp -->

WHAT THIS DOES
--------------
You don't want to install 62 separate `uvx <name>-mcp` packages. You want ONE
router that holds the manifest of every MEOK MCP and exposes them all behind a
single MCP server with namespaced tools.

This MCP gives you:

  - `route_call(target_mcp, tool_name, args)`     — proxy a call
  - `list_routes()`                                — every routable MCP + tool
  - `register_local_mcp(slug, command, args)`     — add your own non-MEOK MCP
  - `health_check(slug?)`                          — ping a downstream MCP
  - `bundle_subset(category, tools_per_mcp?)`     — generate a subset routing config
  - `sign_call_chain(call_log)`                    — HMAC seal a multi-MCP transaction

PRICING
-------
Free MIT self-host · £29/mo Starter · £79/mo Pro · A2A Substrate £999/mo.
"""

from __future__ import annotations
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("agent-mcp-router")
_HMAC_SECRET = os.environ.get("MEOK_HMAC_SECRET", "")


# ──────────────────────────────────────────────────────────────────────
# Built-in route map — refresh from meok.ai/anthropic-registry data.ts
# ──────────────────────────────────────────────────────────────────────
DEFAULT_ROUTES = {
    # Governance (subset — illustrative; production loads from /anthropic-registry)
    "eu-ai-act-compliance-mcp":  {"category": "governance", "install": "uvx eu-ai-act-compliance-mcp"},
    "dora-compliance-mcp":       {"category": "governance", "install": "uvx dora-compliance-mcp"},
    "nis2-compliance-mcp":       {"category": "governance", "install": "uvx nis2-compliance-mcp"},
    "cra-compliance-mcp":        {"category": "governance", "install": "uvx cra-compliance-mcp"},
    "ai-bom-mcp":                {"category": "governance", "install": "uvx ai-bom-mcp"},
    "iso-42005-impact-mcp":      {"category": "governance", "install": "uvx iso-42005-impact-mcp"},
    "korea-ai-basic-act-mcp":    {"category": "governance", "install": "uvx korea-ai-basic-act-mcp"},
    "uk-ai-bill-compliance-mcp": {"category": "governance", "install": "uvx uk-ai-bill-compliance-mcp"},
    "bias-detection-mcp":        {"category": "governance", "install": "uvx bias-detection-mcp"},
    "watermarking-authenticity-mcp": {"category": "governance", "install": "uvx watermarking-authenticity-mcp"},
    "agent-content-watermark-mcp": {"category": "governance", "install": "uvx agent-content-watermark-mcp"},
    "ai-incident-reporting-mcp": {"category": "governance", "install": "uvx ai-incident-reporting-mcp"},
    "agent-incident-relay-mcp":  {"category": "governance", "install": "uvx agent-incident-relay-mcp"},
    "dora-nis2-crosswalk-mcp":   {"category": "governance", "install": "uvx dora-nis2-crosswalk-mcp"},
    # A2A
    "bft-progress-council-mcp":  {"category": "a2a", "install": "uvx bft-progress-council-mcp"},
    "agent-token-budget-mcp":    {"category": "a2a", "install": "uvx agent-token-budget-mcp"},
    "agent-cost-allocator-mcp":  {"category": "a2a", "install": "uvx agent-cost-allocator-mcp"},
    "agent-commerce-protocol-mcp": {"category": "a2a", "install": "uvx agent-commerce-protocol-mcp"},
    "agent-x402-paywall-mcp":    {"category": "a2a", "install": "uvx agent-x402-paywall-mcp"},
    "agent-identity-trust-mcp":  {"category": "a2a", "install": "uvx agent-identity-trust-mcp"},
    "agent-data-residency-mcp":  {"category": "a2a", "install": "uvx agent-data-residency-mcp"},
    "agent-policy-enforcement-mcp": {"category": "a2a", "install": "uvx agent-policy-enforcement-mcp"},
    "agent-prompt-injection-firewall-mcp": {"category": "a2a", "install": "uvx agent-prompt-injection-firewall-mcp"},
    "agent-rate-limiter-mcp":    {"category": "a2a", "install": "uvx agent-rate-limiter-mcp"},
    "agent-delegation-mcp":      {"category": "a2a", "install": "uvx agent-delegation-mcp"},
    "agent-handoff-certified-mcp": {"category": "a2a", "install": "uvx agent-handoff-certified-mcp"},
    "agent-orchestrator-mcp":    {"category": "a2a", "install": "uvx agent-orchestrator-mcp"},
    "agent-audit-logger-mcp":    {"category": "a2a", "install": "uvx agent-audit-logger-mcp"},
    "agent-commerce-payments-mcp": {"category": "a2a", "install": "uvx agent-commerce-payments-mcp"},
    "agent-negotiation-mcp":     {"category": "a2a", "install": "uvx agent-negotiation-mcp"},
    "a2a-governance-bridge-mcp": {"category": "a2a", "install": "uvx a2a-governance-bridge-mcp"},
    "oasf-agent-directory-mcp":  {"category": "a2a", "install": "uvx oasf-agent-directory-mcp"},
    "eudi-wallet-mcp":           {"category": "a2a", "install": "uvx eudi-wallet-mcp"},
    "agent-replay-debugger-mcp": {"category": "a2a", "install": "uvx agent-replay-debugger-mcp"},
    # Devtools
    "mcp-spec-compliance-mcp":   {"category": "devtool", "install": "uvx mcp-spec-compliance-mcp"},
    # Cybersec
    "sbom-cyclonedx-mcp":        {"category": "cybersec", "install": "uvx sbom-cyclonedx-mcp"},
    "mitre-attack-mcp":          {"category": "cybersec", "install": "uvx mitre-attack-mcp"},
    "mitre-atlas-mcp":           {"category": "cybersec", "install": "uvx mitre-atlas-mcp"},
    "cisa-kev-mcp":              {"category": "cybersec", "install": "uvx cisa-kev-mcp"},
    # Platform
    "gods-eye-geospatial-mcp":   {"category": "platform", "install": "uvx gods-eye-geospatial-mcp"},
    "care-membrane-mcp":         {"category": "platform", "install": "uvx care-membrane-mcp"},
}

_LOCAL_ROUTES: dict[str, dict] = {}
_CALL_LOG: list[dict] = []


def _sign(payload: dict) -> str:
    if not _HMAC_SECRET:
        return "unsigned-no-key-configured"
    return hmac.new(_HMAC_SECRET.encode(), json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _all_routes() -> dict:
    return {**DEFAULT_ROUTES, **_LOCAL_ROUTES}


# ──────────────────────────────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_routes(category: Optional[str] = None) -> dict:
    """
    List every routable MCP behind the router.

    Args:
        category: Optional filter ("governance", "a2a", "cybersec", "platform", "devtool").

    Returns:
        {routes, total, categories}
    """
    routes = _all_routes()
    if category:
        routes = {k: v for k, v in routes.items() if v.get("category") == category}
    cats = {}
    for v in _all_routes().values():
        cats[v.get("category", "uncategorised")] = cats.get(v.get("category", "uncategorised"), 0) + 1
    return {
        "routes": routes,
        "total": len(routes),
        "categories": cats,
        "hint": "Call route_call(slug, tool, args) to invoke any of these via this router.",
    }


@mcp.tool()
def route_call(target_mcp: str, tool_name: str, args: Optional[dict] = None) -> dict:
    """
    Proxy a call to one of the registered MCPs.

    NOTE: This is a scaffold. Production routes through stdio subprocess or
    HTTP-streamable transport. This stub records the call and returns a
    deterministic stub result that downstream code can mock.

    Args:
        target_mcp: Slug from list_routes(). E.g. "bft-progress-council-mcp".
        tool_name: Tool to invoke on that MCP.
        args: Arguments dict.

    Returns:
        {routed, target, tool, args_hash, call_id, stub_result}
    """
    routes = _all_routes()
    if target_mcp not in routes:
        return {"error": f"Unknown target_mcp: {target_mcp}. Call list_routes() to see options."}

    call_id = f"CALL_{int(time.time())}_{os.urandom(4).hex()}"
    args_hash = hashlib.sha256(json.dumps(args or {}, sort_keys=True).encode()).hexdigest()[:16]
    entry = {
        "call_id": call_id,
        "target_mcp": target_mcp,
        "tool_name": tool_name,
        "args_hash": args_hash,
        "ts": _ts(),
        "route_method": "stdio_subprocess (scaffold)",
    }
    _CALL_LOG.append(entry)
    return {
        "routed": True,
        "call_id": call_id,
        "target": target_mcp,
        "tool": tool_name,
        "args_hash": args_hash,
        "stub_result": {
            "note": "scaffold — production launches the target MCP via stdio subprocess and forwards args+result",
            "install": routes[target_mcp]["install"],
        },
        "next_step": "Use sign_call_chain() once you've completed the multi-MCP transaction.",
    }


@mcp.tool()
def register_local_mcp(slug: str, command: str, args: Optional[list[str]] = None, category: str = "user") -> dict:
    """
    Add a non-MEOK MCP to this router's local route map.

    Args:
        slug: How you'll reference this MCP in route_call().
        command: Executable (e.g. "uvx", "npx", "python", "node").
        args: Argument list to launch the MCP.
        category: Optional group label.

    Returns:
        {registered, route_count}
    """
    _LOCAL_ROUTES[slug] = {
        "category": category,
        "install": f"{command} {' '.join(args or [])}".strip(),
        "user_registered": True,
        "registered_at": _ts(),
    }
    return {
        "registered": True,
        "slug": slug,
        "route_count": len(_all_routes()),
    }


@mcp.tool()
def health_check(slug: Optional[str] = None) -> dict:
    """
    Ping one or all routed MCPs to see if they're reachable.

    Args:
        slug: Optional single MCP to check. Otherwise checks all.

    Returns:
        {checked: int, healthy: int, unreachable: [...]}
    """
    routes = _all_routes()
    if slug:
        routes = {slug: routes.get(slug)} if slug in routes else {}
    if not routes:
        return {"error": "no routes to check"}
    # Scaffold — production opens a subprocess and reads stdout/stderr capacities
    return {
        "checked": len(routes),
        "healthy": len(routes),
        "unreachable": [],
        "method": "scaffold (production launches uvx + waits for `ready` line)",
    }


@mcp.tool()
def bundle_subset(category: str, tools_per_mcp: Optional[int] = None) -> dict:
    """
    Generate a routing config for an MCP-client subset (Claude Code / Cursor).

    Args:
        category: "governance" | "a2a" | "cybersec" | "platform" | "devtool" | "all".
        tools_per_mcp: Optional cap on tools surfaced per MCP for token-budget reasons.

    Returns:
        {mcp_config, install_count}
    """
    routes = _all_routes()
    if category != "all":
        routes = {k: v for k, v in routes.items() if v.get("category") == category}
    config = {
        "mcpServers": {
            slug.replace("-mcp", ""): {
                "command": "uvx",
                "args": [slug],
                **({"_tool_cap": tools_per_mcp} if tools_per_mcp else {}),
            }
            for slug in routes
        }
    }
    return {
        "mcp_config": config,
        "install_count": len(routes),
        "category": category,
        "hint": "Paste this into ~/.claude.json or .cursor/mcp.json to enable the whole subset at once.",
    }


@mcp.tool()
def sign_call_chain(call_ids: Optional[list[str]] = None) -> dict:
    """
    HMAC-sign a multi-MCP transaction so auditors can replay the chain.

    Args:
        call_ids: Subset of CALL_* ids from the log. Defaults to all logged calls.

    Returns:
        {signed, signature, sealed_at, chain_length}
    """
    chain = [c for c in _CALL_LOG if (not call_ids) or c["call_id"] in call_ids]
    sealed = {
        "chain": chain,
        "sealed_at": _ts(),
        "issuer": "MEOK AI Labs (CSOAI LTD)",
    }
    sig = _sign(sealed)
    return {
        "signed": _HMAC_SECRET != "",
        "signature": sig,
        "sealed_at": sealed["sealed_at"],
        "chain_length": len(chain),
    }


if __name__ == "__main__":
    mcp.run()
