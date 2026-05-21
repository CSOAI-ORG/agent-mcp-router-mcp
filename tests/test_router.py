"""Smoke tests for agent-mcp-router-mcp."""
import sys, os, inspect, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    list_routes,
    route_call,
    register_local_mcp,
    health_check,
    bundle_subset,
    sign_call_chain,
    DEFAULT_ROUTES,
    _LOCAL_ROUTES,
    _CALL_LOG,
)


def test_list_routes_returns_all():
    _LOCAL_ROUTES.clear()
    r = list_routes()
    assert r["total"] >= 30
    assert "governance" in r["categories"]
    assert "a2a" in r["categories"]


def test_list_routes_filter_by_category():
    _LOCAL_ROUTES.clear()
    r = list_routes(category="governance")
    assert all(v["category"] == "governance" for v in r["routes"].values())
    assert r["total"] >= 10


def test_route_call_records_call_log():
    _CALL_LOG.clear()
    r = route_call("bft-progress-council-mcp", "register_run", {"goal": "test"})
    assert r["routed"] is True
    assert r["call_id"].startswith("CALL_")
    assert len(_CALL_LOG) == 1


def test_route_call_unknown_target():
    r = route_call("nope-mcp", "tool", {})
    assert "error" in r


def test_register_local_mcp_extends_routes():
    _LOCAL_ROUTES.clear()
    pre = list_routes()["total"]
    r = register_local_mcp("my-mcp", "uvx", ["my-mcp"], category="user")
    assert r["registered"] is True
    assert list_routes()["total"] == pre + 1


def test_health_check_specific():
    r = health_check("bft-progress-council-mcp")
    assert r["checked"] == 1


def test_health_check_unknown_returns_error():
    r = health_check("nope")
    assert "error" in r


def test_bundle_subset_governance():
    r = bundle_subset("governance")
    assert "mcpServers" in r["mcp_config"]
    assert r["install_count"] >= 10


def test_bundle_subset_all():
    r = bundle_subset("all")
    assert r["install_count"] >= 30


def test_sign_call_chain_emits_signature():
    _CALL_LOG.clear()
    route_call("bft-progress-council-mcp", "x", {})
    route_call("agent-token-budget-mcp", "y", {})
    r = sign_call_chain()
    assert "signature" in r
    assert r["chain_length"] == 2


if __name__ == "__main__":
    g = dict(globals())
    fns = [v for k, v in g.items() if k.startswith("test_") and inspect.isfunction(v)]
    p = f = 0
    for fn in fns:
        try:
            fn(); print(f"OK {fn.__name__}"); p += 1
        except Exception as e:
            print(f"X  {fn.__name__}: {type(e).__name__}: {e}"); traceback.print_exc(); f += 1
    print(f"\n{p} passed, {f} failed")
