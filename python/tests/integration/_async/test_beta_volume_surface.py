import pytest


def test_mcp_client_has_volume_apis():
    from agentbay.api.client import Client

    # We only check method presence here (surface compatibility). End-to-end tests cover behavior.
    for name in ("get_volume_async", "delete_volume_async", "list_volumes_async"):
        assert hasattr(Client, name), f"expected agentbay.api.client.Client to have {name}"


def test_create_mcp_session_request_has_volume_id():
    from agentbay.api.models import CreateMcpSessionRequest

    req = CreateMcpSessionRequest()
    assert hasattr(req, "volume_id"), "expected CreateMcpSessionRequest to have volume_id"

    req.volume_id = "vol-test"
    m = req.to_map()
    assert m.get("VolumeId") == "vol-test"


