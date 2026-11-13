[![MCP Scorecard: 95/100](https://img.shields.io/badge/proofof.ai-95%2F100-5b21b6)](https://proofof.ai/scorecard/agent-mcp-router-mcp.html)

mcp-name: io.github.CSOAI-ORG/agent-mcp-router-mcp

# Agent MCP Router MCP

[![MEOK AI Labs](https://img.shields.io/badge/MEOK-AI%20Labs-667eea)](https://meok.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Install-3775a9)](https://pypi.org/project/agent_mcp_router_mcp/)

> Agent MCP Router MCP - one router for the whole MEOK fleet

Agent MCP Router MCP - one router for the whole MEOK fleet. 62 MCPs behind one connection. MIT. By MEOK AI Labs.

---

## 🚀 Quick Start

```bash
# Install via pip
pip install agent_mcp_router_mcp

# Or install via Smithery
npx -y @smithery/cli@latest install agent-mcp-router-mcp --client claude
```

## ✨ Features

- Multi-MCP routing
- Load balancing
- Health checking
- Fallback handling
- Metrics & observability

## 📖 Documentation

- [Full Documentation](https://docs.meok.ai/agent-mcp-router-mcp)
- [API Reference](https://api.meok.ai)
- [EU AI Act Compliance Guide](https://councilof.ai/compliance)

## 🛡️ Compliance

This MCP server is built with **EU AI Act compliance** built-in:

- ✅ Article 9 — Risk Management System
- ✅ Article 13 — Transparency & Instructions for Use
- ✅ Article 15 — Bias Detection & Testing
- ✅ Article 26 — FRIA Support (where applicable)
- ✅ Article 50 — AI Content Watermarking (where applicable)

Need help getting compliant? **[Book a free 15-min diagnostic →](https://cal.com/csoai/august-audit)**

## How MEOK charges

MEOK has no subscriptions and no tiers. You pay per job, and only when the agreed artifact has been delivered to you. There is no public price list. See <https://meok.ai/pricing>.

This repository's source is MIT-licensed and free to self-host.

## 🤝 Part of the MEOK Ecosystem

This server is part of the **[MEOK AI Labs](https://meok.ai)** ecosystem — 300+ MCP servers for sovereign AI governance.

| Domain | Purpose |
|--------|---------|
| [councilof.ai](https://councilof.ai) | EU AI Act compliance marketplace |
| [safetyof.ai](https://safetyof.ai) | AI safety & monitoring |
| [meok.ai](https://meok.ai) | Sovereign AI platform |
| [cobolbridge.ai](https://cobolbridge.ai) | Legacy modernization |

## 📜 License

MIT © [CSOAI-ORG](https://github.com/CSOAI-ORG)

---

<p align="center">
  <sub>Built with 💜 by <a href="https://meok.ai">MEOK AI Labs</a> · UK Companies House 16939677</sub>
</p>
MIT. By [MEOK AI Labs](https://meok.ai) (CSOAI LTD, UK Companies House 16939677).



## Configuration

Add to your `claude_desktop_config.json` (Claude Desktop) or your MCP client config:

```json
{
  "mcpServers": {
    "agent-mcp-router-mcp": {
      "command": "uvx",
      "args": ["agent-mcp-router-mcp"]
    }
  }
}
```

Or: `pip install agent-mcp-router-mcp` then run the `agent-mcp-router-mcp` command (stdio transport).

## Examples

Once configured, ask your assistant, for example:
- "Use `list_routes` to …"
- "Use `route_call` to …"
- "Use `register_local_mcp` to …"
