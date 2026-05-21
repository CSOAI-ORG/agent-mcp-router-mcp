# Agent MCP Router MCP

> ## 🧱 Part of the MEOK A2A Substrate (£999/mo) + Universal PAYG (£29/mo)
> See [meok.ai/a2a](https://meok.ai/a2a).

# One MCP. 62 MEOK MCPs behind it.

<!-- mcp-name: io.github.CSOAI-ORG/agent-mcp-router-mcp -->

[![PyPI](https://img.shields.io/pypi/v/agent-mcp-router-mcp)](https://pypi.org/project/agent-mcp-router-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What this does

You don't want to install 62 separate `uvx <name>-mcp` packages. You want ONE router that holds the manifest of every MEOK MCP and exposes them all behind a single MCP server with namespaced tools.

`uvx agent-mcp-router-mcp` — done. All MEOK MCPs available via one connection.

## Tools

| Tool | Purpose |
|---|---|
| `list_routes(category?)` | Every routable MCP + tool |
| `route_call(target_mcp, tool_name, args)` | Proxy a call to a downstream MCP |
| `register_local_mcp(slug, command, args, category)` | Add your own non-MEOK MCP to the router |
| `health_check(slug?)` | Ping a downstream MCP |
| `bundle_subset(category, tools_per_mcp?)` | Generate a routing config snippet |
| `sign_call_chain(call_ids?)` | HMAC seal a multi-MCP transaction for audit |

## Why this exists

The official MCP Registry has 250+ servers. The 'install everything' problem is real — Claude Code, Cursor, Cline, and Windsurf all hit a tool-count ceiling around 75–100 tools. This router lets you mount the whole MEOK fleet behind one connection slot, with optional `tools_per_mcp` capping so you stay under the ceiling.

You can also register your own (non-MEOK) MCPs to extend the route table.

## Sister MCPs

Part of the MEOK **A2A** pack:

- `bft-progress-council-mcp` — anti-loop guardrail (called before every multi-MCP transaction)
- `agent-token-budget-mcp` — hard spend cap (called by the router for each delegated call)
- `agent-replay-debugger-mcp` — step-debug the router's call chain
- `mcp-spec-compliance-mcp` — lint the MCPs you register against the official spec

Full catalogue: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)

## Pricing

| Option | Price |
|---|---|
| Self-host MIT | £0 |
| Universal PAYG | £29/mo + £0.0002/call |
| A2A Substrate | £999/mo |
| Universe | £1,499/mo |
| Defence | £4,990/mo |

Buy: https://meok.ai/a2a

## Licence

MIT. By [MEOK AI Labs](https://meok.ai) (CSOAI LTD, UK Companies House 16939677).
